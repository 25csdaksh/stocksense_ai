import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const dir = process.cwd();
const files = fs.readdirSync(dir).filter(f => f.endsWith('.tgz'));

for (const file of files) {
  // e.g. postcss-selector-parser-6.1.0.tgz -> postcss-selector-parser
  const pkgName = file.replace(/-[0-9].*$/, '');
  const targetDir = path.join(dir, 'node_modules', pkgName);
  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }
  const fullPath = path.join(dir, file);
  console.log(`Extracting ${file} -> node_modules/${pkgName}`);
  execSync(`tar -xzf "${fullPath}" -C "${targetDir}" --strip-components=1`);
  fs.unlinkSync(fullPath);
}
console.log('Unpacking complete!');
