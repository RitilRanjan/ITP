const fs = require('fs');

const code = fs.readFileSync('app.py', 'utf8');
const scriptMatch = code.match(/<script>([\s\S]*?)<\/script>/);
if (scriptMatch) {
    try {
        new Function(scriptMatch[1]);
        console.log("Syntax is OK!");
    } catch (e) {
        console.error("Syntax Error:", e.message);
    }
}
