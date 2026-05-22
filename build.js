const fs = require('fs');
const path = require('path');

const jsonPath = path.join(__dirname, 'semba_mba_khung.json');
const templatePath = path.join(__dirname, 'template.html');
const outputPath = path.join(__dirname, 'index.html');

try {
  console.log('Reading JSON data from semba_mba_khung.json...');
  const rawJson = fs.readFileSync(jsonPath, 'utf8');
  // Validate JSON
  const jsonData = JSON.parse(rawJson);
  
  console.log('Reading HTML template...');
  let template = fs.readFileSync(templatePath, 'utf8');
  
  const embeddedDataJs = `const EMBEDDED_DATA = ${JSON.stringify(jsonData, null, 2)};`;
  
  console.log('Injecting JSON data into template...');
  template = template.replace('/* {{DATA_PLACEHOLDER}} */', embeddedDataJs);
  
  console.log('Writing final index.html...');
  fs.writeFileSync(outputPath, template, 'utf8');
  
  console.log('\x1b[32m%s\x1b[0m', '✔ Build completed successfully! Created index.html');
} catch (error) {
  console.error('\x1b[31m%s\x1b[0m', '✖ Build failed:', error.message);
  process.exit(1);
}
