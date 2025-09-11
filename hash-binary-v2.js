// Usage: node hash-binary-crc32.js <path>
const fs = require("fs");
const path = require("path");
const CRC32 = require("crc-32"); // npm install crc-32

async function recursivelyHashPath(targetPath, relativeTo = targetPath) {
  const fileHashes = {};
  const queue = [targetPath];

  while (queue.length > 0) {
    const current = queue.pop();
    const stat = fs.statSync(current);
    const relPath = path.relative(relativeTo, current);

    if (stat.isDirectory()) {
      const entries = fs.readdirSync(current).sort().reverse();
      for (const entry of entries) {
        queue.push(path.join(current, entry));
      }
    } else if (stat.isFile()) {
      // Skip AppleDouble + .pyc files
      if (/\/\._/.test(relPath)) continue;
      if (relPath.endsWith(".pyc")) continue;

      const buffer = fs.readFileSync(current);
      // CRC32.buf returns signed 32-bit int; we convert to unsigned and hex
      const signed = CRC32.buf(buffer);
      const unsigned = signed >>> 0; // convert to unsigned
      const hex = unsigned.toString(16).padStart(8, "0");

      fileHashes[relPath] = hex;
    }
  }

  return fileHashes;
}

async function getChecksumsForBinaryPath(binaryFilePath) {
  try {
    return await recursivelyHashPath(binaryFilePath);
  } catch (err) {
    console.error("Error:", err);
    return {};
  }
}

// --- CLI Entry Point ---
(async () => {
  const [, , targetPath] = process.argv;

  if (!targetPath) {
    console.error("Usage: node hash-binary-crc32.js <path>");
    process.exit(1);
  }

  const manifest = await getChecksumsForBinaryPath(targetPath);

  const stat = fs.statSync(targetPath);
  let outFile;

  if (stat.isDirectory()) {
    outFile = path.join(targetPath, "checksums.json");
  } else {
    outFile = path.join(process.cwd(), "checksums.json");
  }

  fs.writeFileSync(outFile, JSON.stringify(manifest, null, 2), "utf-8");
  console.log(`CRC32 manifest written to ${outFile}`);
})();
