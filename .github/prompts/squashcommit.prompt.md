---
agent: 'agent'
description: 'Squash all commits after a specific commit into a single commit with a specific message and force push the changes.'
---

To squash all commits after a specific commit into a single commit with a specific message and force push the changes, you can use the following Git commands:

```shell
SPECIFIC_COMMIT_HASH="4442fca" # Replace with the actual commit hash of the specific commit
COMMIT_MESSAGE="update" # Replace with the desired commit message

git reset --soft $SPECIFIC_COMMIT_HASH && git commit -m "$COMMIT_MESSAGE"
```
