
## Git Flow:

1. Checkout the latest master:

```bash
git checkout master
git pull
```

2. Branch off of master:

```bash
# example: jenny-tru/54 or jenny-tru/quick-fix-for-thing
git checkout -b <USERNAME>/<ISSUE>
```

3. Make your changes!

4. Run tests:

```bash
pytest
# To see print() output:
pytest -s
```

5. Commit your changes, through the VS Code UI or:

```bash
git commit -a -m "Your commit message here"
```

6. Push to origin, through the VS Code UI or:

```bash
git push origin head
```
