// Usage: node hash-binary.js <path>
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

async function recursivelyHashPath(targetPath, relativeTo = targetPath) {
  const fileHashes = {}; // BagIt-style manifest
  const queue = [targetPath];

  while (queue.length > 0) {
    const current = queue.pop();
    const stat = fs.statSync(current);
    const relPath = path.relative(relativeTo, current);

    if (stat.isDirectory()) {
      const entries = fs.readdirSync(current).sort().reverse(); // consistent order
      for (const entry of entries) {
        queue.push(path.join(current, entry));
      }
    } else if (stat.isFile()) {
      // Skip AppleDouble + .pyc files
      if (/\/\._/.test(relPath)) continue;
      if (relPath.endsWith('.pyc')) continue;

      // Hash the file itself
      const fileBuffer = fs.readFileSync(current);
      const fileHash = crypto.createHash('sha256').update(fileBuffer).digest('hex');

      // Save relative path -> hash
      fileHashes[relPath] = fileHash;
    }
  }

  return fileHashes;
}

async function getChecksumsForBinaryPath(binaryFilePath) {
  try {
    return await recursivelyHashPath(binaryFilePath);
  } catch (err) {
    console.error('Error:', err);
    return {};
  }
}

// --- CLI Entry Point ---
(async () => {
  const [, , targetPath] = process.argv;

  if (!targetPath) {
    console.error('Usage: node hash-binary.js <path>');
    process.exit(1);
  }

  const manifest = await getChecksumsForBinaryPath(targetPath);

  const stat = fs.statSync(targetPath);
  let outFile;

  if (stat.isDirectory()) {
    // Write inside the target directory
    outFile = path.join(targetPath, 'checksums.json');
  } else {
    // Write in current working directory
    outFile = path.join(process.cwd(), 'checksums.json');
  }

  fs.writeFileSync(outFile, JSON.stringify(manifest, null, 2), 'utf-8');
  console.log(`BagIt-style manifest written to ${outFile}`);
})();
