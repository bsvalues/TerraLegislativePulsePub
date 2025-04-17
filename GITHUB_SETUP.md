# GitHub Repository Setup Guide

Follow these steps to set up your GitHub repository for the Benton County Assessor AI Platform:

## 1. Create a New Repository on GitHub

1. Go to [GitHub](https://github.com/) and sign in to your account
2. Click on the "+" icon in the top-right corner and select "New repository"
3. Enter a name for your repository (e.g., "benton-county-assessor-ai")
4. Add a short description: "AI-driven legislative tracking platform for Benton County property stakeholders"
5. Choose "Public" for the repository visibility
6. Do NOT initialize with a README, .gitignore, or license (we'll add these ourselves)
7. Click "Create repository"

## 2. Push Your Code to GitHub

After creating the repository, GitHub will display instructions for pushing an existing repository. Follow these commands:

```bash
# Initialize git in your project folder (if not already initialized)
git init

# Add all files to be tracked
git add .

# Commit the files
git commit -m "Initial commit"

# Add the GitHub repository as a remote
git remote add origin https://github.com/YOUR_USERNAME/benton-county-assessor-ai.git

# Push the code to GitHub
git push -u origin main
```

Note: If you're using an older version of Git, you might need to use `master` instead of `main`:

```bash
git push -u origin master
```

## 3. Verify Repository Setup

1. Refresh your GitHub repository page
2. You should see all your files, including the README.md, LICENSE, and other files
3. The README content should be displayed on the main page of your repository

## 4. Set Up Branch Protection (Optional)

For added security and collaboration:

1. Go to your repository on GitHub
2. Click on "Settings" > "Branches"
3. Under "Branch protection rules," click "Add rule"
4. Enter "main" as the branch name pattern
5. Check options like "Require pull request reviews before merging" and "Require status checks to pass before merging"
6. Click "Create" to save your branch protection rule

## 5. Enable GitHub Pages (Optional)

If you want to create a project website:

1. Go to your repository on GitHub
2. Click on "Settings" > "Pages"
3. Under "Source," select "main" branch and "/docs" folder
4. Click "Save"
5. Your site will be published at `https://YOUR_USERNAME.github.io/benton-county-assessor-ai/`

## 6. Add GitHub Actions (Optional)

You can also set up automatic testing or deployment using GitHub Actions:

1. In your repository, create a `.github/workflows` directory
2. Add a workflow file like `python-tests.yml` for running tests

## 7. Inviting Collaborators (Optional)

To invite collaborators to your repository:

1. Go to your repository on GitHub
2. Click on "Settings" > "Manage access"
3. Click "Invite a collaborator"
4. Enter the GitHub username, full name, or email address of the person you want to invite
5. Select their role (Admin, Maintain, Write, Triage, or Read)
6. Click "Add NAME to this repository"