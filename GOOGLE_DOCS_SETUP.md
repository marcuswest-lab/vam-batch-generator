# Google Docs Integration — Setup Guide

**One person sets this up once. Everyone else just uses the dashboard.**

This connects your VAM Dashboard to Google Docs so you can generate formatted briefs directly as Google Docs (no .docx upload/conversion needed).

---

## What You Need

- A Google account (personal or Workspace/business — both work)
- 10 minutes for initial setup

## What You DON'T Need

- Google Cloud Console access
- API keys or service accounts
- Anything installed on team members' machines
- Admin permissions

---

## Step 1: Create the Apps Script Project

1. Go to [script.google.com](https://script.google.com)
2. Click **New project**
3. Delete the default code in `Code.gs`
4. Open the file `google_apps_script/Code.gs` from this project folder
5. Copy the entire contents and paste it into the Apps Script editor
6. Click the project name at the top (says "Untitled project") and rename it to **VAM Brief Generator**
7. Press **Ctrl+S** (or Cmd+S) to save

## Step 2: Set Up a Shared Folder (Optional but Recommended)

This puts all generated briefs in one shared folder your team can access.

1. In Google Drive, create a new folder (e.g., "VAM Creative Briefs")
2. Share the folder with your team
3. Open the folder and copy the folder ID from the URL:
   ```
   https://drive.google.com/drive/folders/THIS_IS_THE_FOLDER_ID
   ```
4. Back in Apps Script, go to **Project Settings** (gear icon on the left)
5. Scroll to **Script Properties** and click **Add script property**
6. Set:
   - Property: `FOLDER_ID`
   - Value: (paste the folder ID)
7. Click **Save script properties**

## Step 3: Test It

1. In the Apps Script editor, select the function **testSetup** from the dropdown at the top
2. Click **Run**
3. If prompted, authorize the script (it needs access to Google Drive and Docs)
4. Check the **Execution log** at the bottom — it should show your folder name
5. Now select **testCreateDoc** and click **Run**
6. Check the Execution log for a Google Doc URL
7. Open the URL — you should see a formatted test brief

## Step 4: Deploy as Web App

1. Click **Deploy** (top right) > **New deployment**
2. Click the gear icon next to "Select type" and choose **Web app**
3. Set:
   - **Description:** VAM Brief Generator
   - **Execute as:** Me
   - **Who has access:** Anyone *(or "Anyone within [your organization]" for extra security)*
4. Click **Deploy**
5. **Copy the Web app URL** — you'll need this for the dashboard

> The URL looks like: `https://script.google.com/macros/s/AKfycb.../exec`

## Step 5: Connect the Dashboard

1. Open your VAM Dashboard (http://localhost:8090)
2. Scroll to **Step 2: Generate Doc**
3. Click **Google Doc Setup**
4. Paste the Web app URL from Step 4
5. Click **Save URL**
6. You should see a green "Connected" indicator

## Step 6: Share with Your Team

Just share the Web app URL with your team members. Each person:

1. Opens their VAM Dashboard
2. Clicks "Google Doc Setup" in Step 2
3. Pastes the same URL
4. Clicks Save

That's it. No other setup needed on their machines.

---

## How It Works

When someone clicks "Generate Google Doc" on the dashboard:

1. The dashboard sends the parsed brief data to your local server
2. The server forwards it to the Google Apps Script
3. The Apps Script creates a new Google Doc with all the content formatted
4. The doc appears in your shared Drive folder
5. The dashboard opens the doc in a new tab

The document includes:
- Properly formatted overview and creative sections
- Color-coded tags for dropdown fields (Variation Type, Awareness Level, Lead Type, Status)
- All copy, notes, and design notes filled in
- Header with client name, campaign name, and date

**Note on dropdowns:** Google's API doesn't support creating interactive dropdown chips programmatically. The dropdown field values are shown as color-coded tags instead. If you need interactive dropdowns, you can add them manually using Insert > Dropdown in Google Docs, or start from a template that already has them.

---

## Updating the Script

If you need to update the Apps Script code later:

1. Go to [script.google.com](https://script.google.com) and open the project
2. Update the code in `Code.gs`
3. Click **Deploy** > **Manage deployments**
4. Click the pencil icon on your deployment
5. Change **Version** to "New version"
6. Click **Deploy**

The URL stays the same — no need to update anyone's dashboard.

---

## Troubleshooting

**"Failed to reach Apps Script"**
- Make sure the deployment URL is correct (ends with `/exec`)
- Make sure the script is deployed as a Web app with "Anyone" access
- Try redeploying with a new version

**"FOLDER_ID not set"**
- This is optional. Without it, docs are created in the deployer's My Drive root
- To set it: Apps Script > Project Settings > Script Properties

**"Authorization required"**
- When you first run the script, Google asks for permissions
- Click "Review permissions" > choose your account > "Allow"
- This only happens once

**Team member can't access generated docs**
- Make sure the output folder (FOLDER_ID) is shared with the team
- Or share individual docs after creation

**"TypeError: Cannot read properties of null"**
- Usually means the data sent to the script is malformed
- Make sure you're pasting complete Claude output (with === CREATIVE N === sections)
