/* AW1 — runner. The UI checks need a real browser, so this wraps the Playwright suite (tests/run_tests_aw1.py) and exits with its status. Run: node tests/aw1_test.js */
const { spawnSync } = require('child_process');
const path = require('path');
const r = spawnSync('python3', ['run_tests_aw1.py'], { cwd: __dirname, stdio: 'inherit' });
if (r.error) { console.log('FAIL - could not start python3 / playwright :: ' + r.error.message); process.exit(1); }
process.exit(r.status === null ? 1 : r.status);
