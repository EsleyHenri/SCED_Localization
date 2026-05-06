useLibrary('threads');
importClass(java.io.File);
importClass(java.util.UUID);
importClass(arkham.project.ProjectUtilities);
importClass(arkham.sheet.RenderTarget);
importClass(ca.cgjennings.apps.arkham.project.Project);
importClass(ca.cgjennings.seplugins.csv.CsvFactory);
importClass(ca.cgjennings.imageio.SimpleImageWriter);

const PROJECT_FOLDER = 'SE_Generator';
const TEMPLATE_FOLDER = 'template';
const DATA_FOLDER = 'data';
const CARD_FOLDER = 'cards';
const IMAGE_FOLDER = 'images';

let headless = Eons.getScriptRunner() !== null;
let project = headless ? Project.open(new File(PROJECT_FOLDER)) : Eons.getOpenProject();

// Build list of {packCode, type} entries by scanning data/{pack_code}/*.csv
let entries = [];
let dataFolder = new File(project.getFile(), DATA_FOLDER);
let packFolders = dataFolder.listFiles();
if (packFolders !== null) {
    for (let p = 0; p < packFolders.length; p++) {
        let packFolder = packFolders[p];
        if (!packFolder.isDirectory()) continue;
        let packCode = packFolder.getName();
        let dataFiles = packFolder.listFiles();
        if (dataFiles !== null) {
            for (let i = 0; i < dataFiles.length; i++) {
                let dataFilename = dataFiles[i].getName();
                if (dataFilename.endsWith('.csv')) {
                    let type = dataFilename.replace('.csv', '');
                    entries.push({packCode: packCode, type: type});
                }
            }
        }
    }
}

// Collect unique pack codes preserving discovery order
let packCodes = [];
for (let i = 0; i < entries.length; i++) {
    let pc = entries[i].packCode;
    if (packCodes.indexOf(pc) === -1) {
        packCodes.push(pc);
    }
}

function process(progress) {
    function syncProject() {
        if (!headless) {
            project.synchronizeAll();
        }
    }

    function reportStatus(progress, status) {
        if (headless) {
            println(status);
        } else {
            progress.status = status;
        }
    }

    let factory = new CsvFactory();
    factory.setDelimiter(',');
    factory.setQuote('"');
    factory.setExtraSpaceIgnored(false);
    factory.setIgnoreUnknownKeys(true);
    factory.setTemplateClearedForEachRow(true);

    let imageWriter = new SimpleImageWriter('png');

    for (let p = 0; !progress.cancelled && p < packCodes.length; p++) {
        let packCode = packCodes[p];

        // Prepare cards/{pack_code}/ subfolder
        let cardFolder = new File(new File(project.getFile(), CARD_FOLDER), packCode);
        ProjectUtilities.deleteAll(cardFolder);
        cardFolder.mkdirs();
        syncProject();

        factory.setOutputFolder(cardFolder);

        // Process all CSVs for this pack
        for (let i = 0; !progress.cancelled && i < entries.length; i++) {
            if (entries[i].packCode !== packCode) continue;
            let type = entries[i].type;
            let templateFile = new File(project.getFile(), TEMPLATE_FOLDER + '/' + type + '.eon');
            let template = ResourceKit.getGameComponentFromFile(templateFile, true);
            let csvFile = new File(project.getFile(), DATA_FOLDER + '/' + packCode + '/' + type + '.csv');
            reportStatus(progress, 'Processing ' + packCode + '/' + csvFile.getName() + '...');
            let csv = ProjectUtilities.getFileText(csvFile, 'utf-8');
            factory.process(template, csv);
            syncProject();
        }

        // Render .eon files to images/{pack_code}/
        let cardFiles = cardFolder.listFiles();
        if (cardFiles === null) continue;

        let imagePackFolder = new File(new File(project.getFile(), IMAGE_FOLDER), packCode);
        if (imagePackFolder.exists()) {
            imagePackFolder.renameTo(new File(new File(project.getFile(), IMAGE_FOLDER), packCode + '-' + UUID.randomUUID().toString()));
            imagePackFolder = new File(new File(project.getFile(), IMAGE_FOLDER), packCode);
        }
        imagePackFolder.mkdirs();
        syncProject();

        for (let i = 0; !progress.cancelled && i < cardFiles.length; i++) {
            let cardFile = cardFiles[i];
            let card = ResourceKit.getGameComponentFromFile(cardFile, true);
            let cardFilename = cardFile.getName();
            let fields = cardFilename.replace('.eon', '').split('-');
            let lastField = fields[fields.length - 1];
            let index = lastField === 'T' ? parseInt(fields[fields.length - 2]) : parseInt(lastField);
            let ppi = 300;
            let synthesizeBleedMargin = false;
            let imageFile = new File(imagePackFolder, cardFilename.replace('.eon', '.png'));
            reportStatus(progress, 'Generating ' + packCode + '/' + imageFile.getName() + '...');
            let sheets = card.createDefaultSheets();
            let sheet = sheets[index];
            let image = sheet.paint(RenderTarget.EXPORT, ppi, synthesizeBleedMargin);
            imageWriter.write(image, imageFile);
            syncProject();
        }
    }
}

if (headless) {
    process({cancelled: false});
    project.close();
} else {
    Thread.busyWindow(process, 'Building...', true);
}
