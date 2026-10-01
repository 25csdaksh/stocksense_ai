import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);

function unpackAll() {
  const dir = process.cwd();
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.tgz'));
  for (const file of files) {
    // regex to strip version: e.g. util-deprecate-1.0.2.tgz -> util-deprecate
    let pkgName = file.replace(/-[0-9].*$/, '');
    const targetDir = path.join(dir, 'node_modules', pkgName);
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }
    const fullPath = path.join(dir, file);
    try {
      execSync(`tar -xzf "${fullPath}" -C "${targetDir}" --strip-components=1`, { stdio: 'ignore' });
      fs.unlinkSync(fullPath);
      console.log(`Unpacked ${pkgName}`);
    } catch (e) {
      console.error(`Failed to unpack ${file}:`, e.message);
    }
  }
}

function installPkg(pkg) {
  console.log(`Packing & installing: ${pkg}`);
  try {
    execSync(`npm pack ${pkg}`, { stdio: 'inherit' });
    unpackAll();
  } catch (e) {
    console.error(`Error packing ${pkg}:`, e.message);
  }
}

const testModules = ['tailwindcss', 'autoprefixer', 'postcss', 'lucide-react', 'clsx', 'tailwind-merge'];

for (let iter = 0; iter < 40; iter++) {
  let allGood = true;
  for (const mod of testModules) {
    try {
      require(mod);
    } catch (e) {
      console.log(`Module ${mod} failed with: ${e.message}`);
      let missing = null;
      if (e.code === 'MODULE_NOT_FOUND') {
        const m = e.message.match(/Cannot find module ['"]([^'"]+)['"]/);
        if (m) {
          missing = m[1];
          if (missing.includes('node_modules')) {
            const parts = missing.split('node_modules');
            const sub = parts[parts.length - 1].replace(/^[\\\/]/, '').split(/[\\\/]/)[0];
            missing = sub;
          }
        }
      }
      if (missing && !missing.startsWith('.')) {
        console.log(`Identified missing dependency: ${missing}`);
        installPkg(missing);
        allGood = false;
        break;
      } else {
        console.error(`Unresolvable error for ${mod}:`, e);
      }
    }
  }
  if (allGood) {
    console.log('All test modules loaded successfully!');
    break;
  }
}
