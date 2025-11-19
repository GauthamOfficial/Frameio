// Script to clean Next.js cache
const fs = require('fs');
const path = require('path');

const nextDir = path.join(__dirname, '.next');

if (fs.existsSync(nextDir)) {
  console.log('Removing .next directory...');
  fs.rmSync(nextDir, { recursive: true, force: true });
  console.log('✓ .next directory removed');
} else {
  console.log('.next directory does not exist');
}

console.log('\nPlease restart your dev server: npm run dev');






