/**
 * VAM Creative Brief — Google Docs Generator
 *
 * Creates formatted Google Docs from VAM Dashboard data.
 * One-time deployment as a Web App — all team members use via dashboard.
 *
 * SETUP:
 *   1. Create a new Apps Script project at script.google.com
 *   2. Paste this entire file into Code.gs
 *   3. (Optional) Go to Project Settings > Script Properties:
 *      - FOLDER_ID: Google Drive folder ID for generated docs
 *   4. Deploy > New deployment > Web app
 *      - Execute as: Me
 *      - Who has access: Anyone (or Anyone in your organization)
 *   5. Copy the deployment URL and paste it into your VAM Dashboard settings
 */

// =====================================================================
// WEB APP HANDLERS
// =====================================================================

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var result = createBriefDocument(data);
    return ContentService.createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: error.message
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: 'ok',
    message: 'VAM Brief Generator is running. Send a POST request with brief data.'
  })).setMimeType(ContentService.MimeType.JSON);
}

// =====================================================================
// MAIN DOCUMENT CREATION
// =====================================================================

function createBriefDocument(data) {
  var batchType = data.batch_type || 'static';
  var client = data.client || 'Value Added Moving';
  var campaignName = data.campaign_name || 'Creative Brief';
  var date = data.date || Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'MM-dd-yyyy');

  // Build document title to match BAD Marketing format
  var typeLabel = batchType.charAt(0).toUpperCase() + batchType.slice(1);
  var docTitle = typeLabel + ' Ad Brief for ' + client + ' ' + campaignName;

  // Create new document
  var doc = DocumentApp.create(docTitle);
  var body = doc.getBody();

  // Move to shared folder if configured
  var folderId = PropertiesService.getScriptProperties().getProperty('FOLDER_ID');
  if (folderId) {
    try {
      var file = DriveApp.getFileById(doc.getId());
      var folder = DriveApp.getFolderById(folderId);
      file.moveTo(folder);
    } catch (e) {
      Logger.log('Could not move to folder: ' + e.message);
    }
  }

  // Clear default content and set margins
  body.clear();
  body.setMarginTop(36);
  body.setMarginBottom(36);
  body.setMarginLeft(54);
  body.setMarginRight(54);

  // Add document header
  var header = doc.addHeader();
  var headerPara = header.appendParagraph(docTitle);
  headerPara.setAlignment(DocumentApp.HorizontalAlignment.LEFT);
  headerPara.editAsText()
    .setFontSize(11)
    .setFontFamily('Arial')
    .setBold(true)
    .setForegroundColor('#374151');

  var datePara = header.appendParagraph(date);
  datePara.setAlignment(DocumentApp.HorizontalAlignment.LEFT);
  datePara.editAsText()
    .setFontSize(9)
    .setFontFamily('Arial')
    .setBold(false)
    .setForegroundColor('#6b7280');

  // Build document based on batch type
  var overview = data.overview || {};
  var creatives = data.creatives || [];

  if (batchType === 'video') {
    buildVideoDoc(body, overview, creatives);
  } else if (batchType === 'copy') {
    buildCopyDoc(body, overview, creatives);
  } else {
    buildStaticDoc(body, overview, creatives);
  }

  doc.saveAndClose();

  return {
    success: true,
    url: doc.getUrl(),
    id: doc.getId(),
    name: docTitle
  };
}

// =====================================================================
// DOCUMENT BUILDERS — one per batch type
// =====================================================================

function buildStaticDoc(body, overview, creatives) {
  addSectionHeading(body, 'OVERVIEW');

  var overviewFields = [
    ['AI Allowed?', overview['AI Allowed?'] || 'Yes, AI Is Allowed', true],
    ['Photo Folder', overview['Photo Folder'] || '', false],
    ['Reference', overview['Reference'] || '', false],
    ['Idea Name', overview['Idea Name'] || '', false],
    ['Angle Name', overview['Angle Name'] || '', false],
    ['Style Name', overview['Style Name'] || '', false],
    ['Task', overview['Task'] || '', false],
    ['General Notes', overview['General Notes'] || '', false],
    ['Design Notes', overview['Design Notes'] || '', false],
    ['Link to Brand Assets', overview['Link to Brand Assets'] || '', false],
    ['Ratio Format(s)', overview['Ratio Format(s)'] || overview['Ratio Format'] || '', false],
    ['Ad Platform', overview['Ad Platform'] || 'All', true],
    ['Avatar', overview['Avatar'] || '', false],
    ['Brand Voice', overview['Brand Voice'] || '', false],
    ['Net New/Iteration', overview['Net New/Iteration'] || '', true],
    ['Landing Page URL', overview['Landing Page URL'] || '', false],
    ['Conversion Objective', overview['Conversion Objective'] || '', false],
    ['Copywriter', overview['Copywriter'] || 'Nate', false]
  ];

  addFieldTable(body, overviewFields);

  var creativeFieldNames = [
    'File Name', 'File', 'Notes', 'Design Notes',
    'Variation Type', 'Awareness Level', 'Lead Type', 'Status', 'Copy'
  ];
  var tagFieldNames = ['Variation Type', 'Awareness Level', 'Lead Type', 'Status'];

  for (var i = 0; i < creatives.length && i < 5; i++) {
    addCreativeSection(body, creatives[i], i + 1, creativeFieldNames, tagFieldNames);
  }
}

function buildVideoDoc(body, overview, creatives) {
  addSectionHeading(body, 'OVERVIEW');

  var overviewFields = [
    ['Video Type', overview['Video Type'] || '', true],
    ['AI Allowed?', overview['AI Allowed?'] || 'Yes, AI Is Allowed', true],
    ['Footage Folder', overview['Footage Folder'] || overview['Photo Folder'] || '', false],
    ['Idea Name', overview['Idea Name'] || '', false],
    ['Angle Name', overview['Angle Name'] || '', false],
    ['Style Name', overview['Style Name'] || '', false],
    ['Task', overview['Task'] || '', false],
    ['General Notes', overview['General Notes'] || '', false],
    ['Editing Notes', overview['Editing Notes'] || '', false],
    ['Link to Brand Assets', overview['Link to Brand Assets'] || '', false],
    ['Any Other Relevant Assets', overview['Any Other Relevant Assets'] || '', false],
    ['Ratio Format(s)', overview['Ratio Format(s)'] || overview['Ratio Format'] || '', false],
    ['Ad Platform', overview['Ad Platform'] || 'All', true],
    ['Avatar', overview['Avatar'] || '', false],
    ['Brand Voice', overview['Brand Voice'] || '', false],
    ['Net New/Iteration', overview['Net New/Iteration'] || '', true],
    ['Landing Page URL', overview['Landing Page URL'] || '', false],
    ['Conversion Objective', overview['Conversion Objective'] || '', false],
    ['Copywriter', overview['Copywriter'] || 'Nate', false]
  ];

  addFieldTable(body, overviewFields);

  var creativeFieldNames = [
    'File Name', 'Video File', 'Notes', 'Editing Notes',
    'Variation Type', 'Awareness Level', 'Lead Type', 'Status',
    'Lead Script', 'Body Script'
  ];
  var tagFieldNames = ['Variation Type', 'Awareness Level', 'Lead Type', 'Status'];

  for (var i = 0; i < creatives.length && i < 5; i++) {
    addCreativeSection(body, creatives[i], i + 1, creativeFieldNames, tagFieldNames);
  }
}

function buildCopyDoc(body, overview, creatives) {
  addSectionHeading(body, 'OVERVIEW');

  var overviewFields = [
    ['AI Allowed?', overview['AI Allowed?'] || 'Yes, AI Is Allowed', true],
    ['Idea Name', overview['Idea Name'] || '', false],
    ['Angle Name', overview['Angle Name'] || '', false],
    ['Copy Type', overview['Copy Type'] || '', true],
    ['Task', overview['Task'] || '', false],
    ['General Notes', overview['General Notes'] || '', false],
    ['Ad Platform', overview['Ad Platform'] || 'All', true],
    ['Net New/Iteration', overview['Net New/Iteration'] || '', true],
    ['Landing Page URL', overview['Landing Page URL'] || '', false],
    ['Conversion Objective', overview['Conversion Objective'] || '', false],
    ['Copywriter', overview['Copywriter'] || 'Nate', false]
  ];

  addFieldTable(body, overviewFields);

  var creativeFieldNames = [
    'Name', 'Notes', 'Variation Type', 'Awareness Level',
    'Lead Type', 'Status', 'Headline', 'Body Copy'
  ];
  var tagFieldNames = ['Variation Type', 'Awareness Level', 'Lead Type', 'Status'];

  for (var i = 0; i < creatives.length && i < 5; i++) {
    var c = creatives[i];
    // Use File Name as fallback for Name in copy batches
    if (!c['Name'] && c['File Name']) {
      c['Name'] = c['File Name'];
    }
    addCreativeSection(body, c, i + 1, creativeFieldNames, tagFieldNames);
  }
}

// =====================================================================
// DOCUMENT BUILDING HELPERS
// =====================================================================

/**
 * Add a section heading (OVERVIEW, CREATIVE 1, etc.)
 */
function addSectionHeading(body, text) {
  var para = body.appendParagraph(text);
  para.setHeading(DocumentApp.ParagraphHeading.HEADING1);
  para.editAsText()
    .setFontSize(13)
    .setFontFamily('Arial')
    .setBold(true)
    .setForegroundColor('#111827');
  para.setSpacingBefore(16);
  para.setSpacingAfter(4);
}

/**
 * Add a 2-column table of field labels and values.
 * fields: array of [label, value, isTag] triples
 */
function addFieldTable(body, fields) {
  // Build initial data array (label + empty value placeholder)
  var tableData = [];
  for (var i = 0; i < fields.length; i++) {
    tableData.push([fields[i][0], '']);
  }

  var table = body.appendTable(tableData);

  // Style and fill each row
  for (var i = 0; i < fields.length; i++) {
    var label = fields[i][0];
    var value = fields[i][1];
    var isTag = fields[i][2];

    var row = table.getRow(i);

    // --- Label cell (column 0) ---
    var labelCell = row.getCell(0);
    labelCell.setWidth(160);
    labelCell.setBackgroundColor('#f9fafb');
    var labelPara = labelCell.getChild(0).asParagraph();
    labelPara.editAsText()
      .setFontSize(9)
      .setFontFamily('Arial')
      .setBold(true)
      .setForegroundColor('#374151');
    labelPara.setSpacingBefore(2);
    labelPara.setSpacingAfter(2);

    // --- Value cell (column 1) ---
    var valueCell = row.getCell(1);
    var valuePara = valueCell.getChild(0).asParagraph();
    valuePara.setSpacingBefore(2);
    valuePara.setSpacingAfter(2);

    if (!value) continue;

    if (isTag) {
      // Styled tag for dropdown-type fields
      setTagStyle(valuePara, value, label);
    } else {
      // Regular text (handle multi-line)
      var lines = value.split('\n');
      valuePara.setText(cleanMarkdown(lines[0]));
      valuePara.editAsText()
        .setFontSize(9)
        .setFontFamily('Arial')
        .setForegroundColor('#111827');

      for (var j = 1; j < lines.length; j++) {
        var newPara = valueCell.appendParagraph(cleanMarkdown(lines[j]));
        newPara.editAsText()
          .setFontSize(9)
          .setFontFamily('Arial')
          .setForegroundColor('#111827');
        newPara.setSpacingBefore(0);
        newPara.setSpacingAfter(0);
      }
    }
  }

  // Style table borders
  table.setBorderWidth(1);
  table.setBorderColor('#e5e7eb');

  // Add spacer after table
  var spacer = body.appendParagraph('');
  spacer.setSpacingBefore(4);
  spacer.setSpacingAfter(4);
  spacer.editAsText().setFontSize(4);
}

/**
 * Add a creative section (heading + field table)
 */
function addCreativeSection(body, creative, index, fieldNames, tagFieldNames) {
  // Section heading
  var heading = body.appendParagraph('CREATIVE ' + index);
  heading.setHeading(DocumentApp.ParagraphHeading.HEADING2);
  heading.editAsText()
    .setFontSize(12)
    .setFontFamily('Arial')
    .setBold(true)
    .setForegroundColor('#1f2937');
  heading.setSpacingBefore(16);
  heading.setSpacingAfter(4);

  // Build field rows
  var fields = [];
  for (var i = 0; i < fieldNames.length; i++) {
    var fieldName = fieldNames[i];
    var value = creative[fieldName] || '';
    var isTag = tagFieldNames.indexOf(fieldName) !== -1;
    fields.push([fieldName, value, isTag]);
  }

  addFieldTable(body, fields);
}

/**
 * Style text as a colored tag/badge for dropdown-type fields.
 * Colors are chosen based on the field name for visual distinction.
 */
function setTagStyle(paragraph, value, fieldName) {
  var bgColor, fgColor;
  var fn = (fieldName || '').toLowerCase();

  if (fn.indexOf('variation') !== -1) {
    bgColor = '#dbeafe'; fgColor = '#1e40af';  // Blue
  } else if (fn.indexOf('awareness') !== -1) {
    bgColor = '#dcfce7'; fgColor = '#166534';  // Green
  } else if (fn.indexOf('lead type') !== -1) {
    bgColor = '#f3e8ff'; fgColor = '#6b21a8';  // Purple
  } else if (fn.indexOf('status') !== -1) {
    bgColor = '#ffedd5'; fgColor = '#9a3412';  // Orange
  } else {
    bgColor = '#f3f4f6'; fgColor = '#374151';  // Gray
  }

  // Clear existing text and add styled value
  paragraph.setText('');
  var text = paragraph.appendText(' ' + value + ' ');
  text.setFontSize(9)
    .setFontFamily('Arial')
    .setBold(true)
    .setBackgroundColor(bgColor)
    .setForegroundColor(fgColor);
}

/**
 * Strip markdown formatting from text
 */
function cleanMarkdown(text) {
  if (!text) return '';
  // Remove bold markers
  text = text.replace(/\*\*(.+?)\*\*/g, '$1');
  // Remove italic markers
  text = text.replace(/\*(.+?)\*/g, '$1');
  // Remove markdown link syntax [text](url) -> text
  text = text.replace(/\[(.+?)\]\(.+?\)/g, '$1');
  // Remove heading markers
  text = text.replace(/^#{1,6}\s*/gm, '');
  // Convert arrow bullets to regular bullets
  text = text.replace(/^→\s*/gm, '- ');
  return text.trim();
}

// =====================================================================
// SETUP & TESTING HELPERS
// =====================================================================

/**
 * Run this in the Apps Script editor to verify your setup.
 * Go to: Run > testSetup
 */
function testSetup() {
  var props = PropertiesService.getScriptProperties();
  var folderId = props.getProperty('FOLDER_ID');

  Logger.log('=== VAM Brief Generator Setup Check ===');
  Logger.log('');

  if (folderId) {
    try {
      var folder = DriveApp.getFolderById(folderId);
      Logger.log('FOLDER_ID: ' + folderId);
      Logger.log('Folder found: ' + folder.getName());
    } catch (e) {
      Logger.log('FOLDER_ID set but invalid or inaccessible: ' + folderId);
      Logger.log('Check the ID and sharing permissions.');
    }
  } else {
    Logger.log('FOLDER_ID not set (optional).');
    Logger.log('Docs will be created in your My Drive root.');
    Logger.log('To set: Project Settings > Script Properties > Add "FOLDER_ID"');
  }

  Logger.log('');
  Logger.log('Next step: Deploy > New deployment > Web app');
  Logger.log('  Execute as: Me');
  Logger.log('  Who has access: Anyone (or Anyone in your organization)');
}

/**
 * Run this to create a test document and verify everything works.
 * Go to: Run > testCreateDoc
 * Then check the Execution Log for the document URL.
 */
function testCreateDoc() {
  var testData = {
    batch_type: 'static',
    client: 'Value Added Moving',
    campaign_name: 'Test Brief',
    date: Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'MM-dd-yyyy'),
    overview: {
      'AI Allowed?': 'Yes, AI Is Allowed',
      'Task': 'Test document generation — verify the Apps Script works.',
      'Ad Platform': 'All',
      'Net New/Iteration': 'Iteration',
      'Avatar': 'Individuals and families planning a cross-country move',
      'Brand Voice': 'Direct, confident, savings-focused',
      'Landing Page URL': 'https://valueaddedmoving.com/quote',
      'Conversion Objective': 'Lead Generation',
      'Copywriter': 'Nate'
    },
    creatives: [
      {
        'File Name': 'SC999_TestCreative | SV8_Gmail',
        'Notes': 'This is a test creative to verify the Google Docs generator works correctly.',
        'Design Notes': 'Gmail dark mode inbox layout. Standard formatting.',
        'Variation Type': 'Visual',
        'Awareness Level': 'Most Aware',
        'Lead Type': 'Offer',
        'Status': 'Ready For Internal',
        'Copy': 'Subject: "Test headline for verification"\n\nThis is the ad body copy.\n\nLong-distance moves starting at $1,597.\n\nGet your free quote in 60 seconds.'
      }
    ]
  };

  var result = createBriefDocument(testData);
  Logger.log('');
  Logger.log('Test document created successfully!');
  Logger.log('URL: ' + result.url);
  Logger.log('');
  Logger.log('Open the URL above to verify the formatting looks correct.');
}
