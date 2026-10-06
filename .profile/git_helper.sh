#!/usr/bin/env bash

# Display standard usage information
show_help() {
    cat << 'EOF'
usage: git_helper <command> [<args>]

Tool for :

Commands:
  --commit [<msg>]    Commit all local repository changes and push to the GitHub.
                      Outputs a web repository link upon success.
  
  --rollback [<n>]    Reset the local repository state backward by <n> commits.
                      Requires a clean working tree. Defaults to 1 if not specified.

  --sync              Synchronize the local repository with the version on GitHub.
                      Uncommitted changes are automatically preserved in a backup branch.

  --zip               Build a compressed bundle (.zip) storing the repository and development logs.

EOF
}

COMMAND="$1"
ARG="$2"

if [[ -z "$COMMAND" || "$COMMAND" == "--help" || "$COMMAND" == "-h" ]]; then
    show_help
    exit 0
fi

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "fatal: not a git repository (or any of the parent directories)"
    exit 1
fi

if ! git remote get-url origin > /dev/null 2>&1; then
    echo "fatal: no remote repository configured for 'origin'."
    exit 1
fi

get_branch() {
    git rev-parse --abbrev-ref HEAD
}

print_github_links() {
    local branch=$(get_branch)
    local remote_url=$(git config --get remote.origin.url)
    local web_url=""

    # Convert SSH (git@github.com:user/repo.git) to HTTPS format
    if [[ "$remote_url" == git@* ]]; then
        web_url="${remote_url/:/\/}"
        web_url="${web_url/git@/https:\/\/}"
    else
        web_url="$remote_url"
    fi

    # Strip injected access tokens (e.g., Codespaces integration)
    web_url=$(echo "$web_url" | sed -E 's|https://[^@]+@|https://|')
    
    # Remove .git suffix
    web_url="${web_url%.git}"

    echo ""
    echo "Repository URL: $web_url/tree/$branch"
    echo ""
}

case "$COMMAND" in

  --commit)
      
    if [[ -n $(git status --porcelain) ]]; then
        git add .
        MSG="${ARG:-Update $(date +'%Y-%m-%d %H:%M')}"
        if ! git commit -m "$MSG" > /dev/null; then
            echo "error: failed to create commit."
            exit 1
        fi
        echo "info: working directory committed."
    else
        echo "info: working tree clean. Nothing to commit."
    fi

    BRANCH=$(get_branch)
    echo "info: pushing to origin/$BRANCH..."
    
    if ! git push origin "$BRANCH" --force-with-lease > /dev/null 2>&1; then
        echo "error: failed to push to remote. Fetch and integrate remote changes before pushing."
        exit 1
    fi
    
    echo "info: push successful."
    print_github_links
    ;;

  --rollback)
    if [[ -n $(git status --porcelain) ]]; then
        echo "error: working tree has modifications. Run 'git_helper --commit' before rolling back."
        exit 1
    fi

    if ! git fetch origin > /dev/null 2>&1; then
        echo "error: unable to fetch from remote server."
        exit 1
    fi

    BRANCH=$(get_branch)
    LOCAL_HASH=$(git rev-parse HEAD)
    REMOTE_HASH=$(git rev-parse "origin/$BRANCH")

    if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
        AHEAD=$(git rev-list HEAD ^origin/$BRANCH --count)
        if [ "$AHEAD" -gt 0 ]; then
             echo "error: local commits exist that are not present on the remote."
             echo "       Run 'git_helper --commit' to push changes before rolling back."
             exit 1
        fi
    fi

    if [[ -z "$ARG" ]]; then
        COUNT=1
    elif ! [[ "$ARG" =~ ^[0-9]+$ ]]; then
        echo "error: rollback amount must be a positive integer."
        exit 1
    else
        COUNT="$ARG"
    fi

    echo "info: resetting HEAD backward by $COUNT commit(s)..."
    
    if ! git reset --hard "HEAD~$COUNT" > /dev/null; then
        echo "error: failed to reset HEAD. Ensure the specified commit count does not exceed repository history."
        exit 1
    fi
    
    echo "info: rollback complete. Local branch is now at HEAD~$COUNT."
    echo "info: to finalize this state on the remote, run 'git_helper --commit'."
    ;;

  --sync)
    if ! git fetch origin > /dev/null 2>&1; then
        echo "error: unable to fetch from remote server. Synchronization aborted."
        exit 1
    fi

    BRANCH=$(get_branch)
    LOCAL_HASH=$(git rev-parse HEAD)
    REMOTE_HASH=$(git rev-parse "origin/$BRANCH")
    UNCOMMITTED_CHANGES=$(git status --porcelain)

    if [[ "$LOCAL_HASH" == "$REMOTE_HASH" && -z "$UNCOMMITTED_CHANGES" ]]; then
        echo "info: local workspace is already synchronized with origin/$BRANCH."
        exit 0
    fi

    echo "warning: this operation will reset your local repository to match the remote state."
    echo "         Any current work will be archived to a backup branch."
    read -p "Proceed with synchronization? [y/N]: " CONFIRM
    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
        echo "info: operation cancelled."
        exit 0
    fi

    if [[ -n "$UNCOMMITTED_CHANGES" ]]; then
        git add .
        git commit -m "Auto-save before sync $(date)" > /dev/null 2>&1
    fi

    BACKUP_NAME="backup/sync-$(date +%s)"
    
    if ! git push origin HEAD:refs/heads/"$BACKUP_NAME" > /dev/null 2>&1; then
        echo "error: failed to push backup branch to remote. Synchronization halted to preserve data."
        exit 1
    fi
    echo "info: current state secured in remote branch '$BACKUP_NAME'."

    if ! git reset --hard "origin/$BRANCH" > /dev/null; then
        echo "error: failed to reset local repository."
        exit 1
    fi
    
    echo "info: synchronization complete. Local workspace matches origin/$BRANCH."
    print_github_links
    ;;

  --zip)
    echo "info: preparing zip archive..."
    
    if ! grep -q "^*.zip$" .gitignore 2>/dev/null || ! grep -q "^*.bundle$" .gitignore 2>/dev/null; then
        echo "*.zip" >> .gitignore
        echo "*.bundle" >> .gitignore
        git add .gitignore
        git commit -m "chore: ignore archive files" > /dev/null 2>&1 || true
    fi

    if [[ -n $(git status --porcelain) ]]; then
        git add .
        git commit -m "Final Submission $(date +'%Y-%m-%d %H:%M')" > /dev/null 2>&1
        BRANCH=$(get_branch)
        git push origin "$BRANCH" --force-with-lease > /dev/null 2>&1 || true
    fi

    git fetch origin autosave > /dev/null 2>&1 || true

    if ! command -v zip &> /dev/null; then
        sudo apt-get update > /dev/null 2>&1
        sudo apt-get install -y zip > /dev/null 2>&1
    fi

    TIMESTAMP=$(date +'%Y%m%d-%H%M')
    BUNDLE_NAME="history-$TIMESTAMP.bundle"
    ZIP_NAME="submission-$TIMESTAMP.zip"
    
    if git bundle create "$BUNDLE_NAME" --all > /dev/null 2>&1; then
        zip -q "$ZIP_NAME" "$BUNDLE_NAME"
        rm "$BUNDLE_NAME"
        
        echo "info: zip archive generation successful."
        echo ""
        echo "File: $ZIP_NAME"
        echo "Locate the file in your environment's file explorer to download."
    else
        echo "error: failed to generate git bundle."
        exit 1
    fi
    ;;

  *)
    echo "error: unknown command '$COMMAND'"
    show_help
    exit 1
    ;;
esac