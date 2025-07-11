// Usage: node hash-binary.js <path>
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

async function recursivelyHashPath(targetPath, relativeTo = targetPath) {
  const hash = crypto.createHash('sha256');
  const queue = [targetPath];

  while (queue.length > 0) {
    const current = queue.pop();
    const stat = fs.statSync(current);
    const relPath = path.relative(relativeTo, current);

    if (stat.isDirectory()) {
      const entries = fs.readdirSync(current).sort().reverse(); // Match class version
      for (const entry of entries) {
        queue.push(path.join(current, entry));
      }
      hash.update(relPath);
    } else if (stat.isFile()) {
    if (/\/\._/.test(relPath)) continue; // Skip AppleDouble files anywhere in the tree
      hash.update(relPath);
      const fileBuffer = fs.readFileSync(current);
      hash.update(fileBuffer);
    }
  }

  return hash;
}

async function getChecksumForBinaryFile(binaryFilePath) {
  try {
    const hash = await recursivelyHashPath(binaryFilePath);
    return hash.digest('hex');
  } catch (err) {
    console.error('Error:', err);
    return '';
  }
}

// --- CLI Entry Point ---
(async () => {
  const [,, targetPath] = process.argv;

  if (!targetPath) {
    console.error('Usage: node hash-binary.js <path>');
    process.exit(1);
  }

  const checksum = await getChecksumForBinaryFile(targetPath);
  console.log('Checksum:', checksum);
})();
