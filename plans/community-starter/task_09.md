# task_09: Add validate-community-starter job to oneshot CI

## Goal
Add a new CI job that runs the test script from task_08.

## File to edit
`/home/ubuntu/github/oneshot/.github/workflows/ci.yml`

## Job to add
```yaml
validate-community-starter:
  name: Validate Community Starter
  runs-on: ubuntu-latest

  steps:
    - name: Checkout
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: pip

    - name: Install template dependencies
      run: pip install -r templates/community-starter/requirements.txt pytest

    - name: Make script executable
      run: chmod +x scripts/test-community-starter.sh

    - name: Run community-starter validation
      run: ./scripts/test-community-starter.sh
```

## Acceptance criteria
- New job appears in ci.yml
- Follows existing style: no email, fast fail
- Does not change any existing jobs
