const { processTextureFile } = require('molanko-avatar-generator/node');

const optionsJson = process.argv[2];
if (!optionsJson) {
  console.error('Missing options JSON');
  process.exit(1);
}

let options;
try {
  options = JSON.parse(optionsJson);
} catch (e) {
  console.error('Invalid options JSON:', e.message);
  process.exit(1);
}

const chunks = [];
process.stdin.on('data', chunk => chunks.push(chunk));
process.stdin.on('end', async () => {
  try {
    const imageBuffer = Buffer.concat(chunks);
    const canvas = await processTextureFile(imageBuffer, options);
    const outputBuffer = canvas.toBuffer('image/png');
    process.stdout.write(outputBuffer);
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
});

process.stdin.resume();