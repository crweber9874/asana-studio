/**
 * svg-poses.js — Programmatic SVG wireframe generator for yoga poses.
 * Creates minimalist stick-figure line drawings mapped by category/pose name.
 */
const SVGPoses = (() => {
    const STROKE = 'currentColor';
    const SW = 2.5;
    const HEAD_R = 6;

    // Each returns an SVG string inside a viewBox="0 0 100 100"
    const shapes = {
        standing: `
            <circle cx="50" cy="15" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="50" y1="21" x2="50" y2="55" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="35" y1="35" x2="65" y2="35" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="55" x2="40" y2="85" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="55" x2="60" y2="85" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        warrior: `
            <circle cx="50" cy="12" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="50" y1="18" x2="50" y2="50" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="30" y1="28" x2="70" y2="28" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="50" x2="30" y2="55" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="30" y1="55" x2="28" y2="80" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="50" x2="72" y2="80" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        tree: `
            <circle cx="50" cy="12" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="50" y1="18" x2="50" y2="55" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="38" y1="22" x2="50" y2="30" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="62" y1="22" x2="50" y2="30" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="55" x2="50" y2="88" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="65" x2="38" y2="55" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        downdog: `
            <circle cx="28" cy="35" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="30" y1="40" x2="50" y2="22" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="50" y1="22" x2="72" y2="60" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="28" y1="45" x2="22" y2="70" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="72" y1="60" x2="62" y2="82" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="72" y1="60" x2="82" y2="82" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        seated: `
            <circle cx="50" cy="18" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="50" y1="24" x2="50" y2="55" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="35" y1="35" x2="65" y2="35" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="55" x2="30" y2="65" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="30" y1="65" x2="25" y2="55" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="55" x2="70" y2="65" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="70" y1="65" x2="75" y2="55" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        supine: `
            <circle cx="18" cy="60" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="24" y1="60" x2="80" y2="60" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="35" y1="55" x2="35" y2="48" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="40" y1="55" x2="40" y2="50" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="80" y1="60" x2="85" y2="55" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="80" y1="60" x2="85" y2="65" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        backbend: `
            <circle cx="65" cy="25" r="${HEAD_R}" fill="${STROKE}"/>
            <path d="M62 30 Q50 50,50 65" stroke="${STROKE}" stroke-width="${SW}" fill="none"/>
            <line x1="55" y1="40" x2="70" y2="35" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="65" x2="38" y2="85" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="65" x2="62" y2="85" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        inversion: `
            <circle cx="50" cy="82" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="50" y1="76" x2="50" y2="40" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="40" y1="72" x2="60" y2="72" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="40" x2="40" y2="15" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="40" x2="60" y2="15" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        armbalance: `
            <circle cx="35" cy="45" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="38" y1="50" x2="55" y2="55" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="45" y1="55" x2="42" y2="75" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="52" y1="55" x2="55" y2="75" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="55" y1="55" x2="80" y2="50" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="55" y1="55" x2="80" y2="58" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        plank: `
            <circle cx="22" cy="42" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="28" y1="45" x2="78" y2="52" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="30" y1="48" x2="28" y2="68" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="78" y1="52" x2="82" y2="72" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="78" y1="52" x2="76" y2="72" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        twist: `
            <circle cx="50" cy="15" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="50" y1="21" x2="50" y2="55" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="35" y1="32" x2="68" y2="38" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="55" x2="38" y2="82" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="55" x2="62" y2="82" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        balance: `
            <circle cx="50" cy="12" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="50" y1="18" x2="50" y2="50" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="35" y1="25" x2="70" y2="30" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="50" x2="50" y2="85" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="55" x2="75" y2="45" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        lunge: `
            <circle cx="42" cy="12" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="42" y1="18" x2="45" y2="50" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="30" y1="22" x2="55" y2="28" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="45" y1="50" x2="30" y2="55" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="30" y1="55" x2="25" y2="80" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="45" y1="50" x2="72" y2="78" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        forward_fold: `
            <circle cx="50" cy="45" r="${HEAD_R}" fill="${STROKE}"/>
            <path d="M50 50 Q50 55,52 60 L55 70" stroke="${STROKE}" stroke-width="${SW}" fill="none"/>
            <line x1="48" y1="50" x2="42" y2="72" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="55" y1="70" x2="45" y2="88" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="55" y1="70" x2="65" y2="88" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        kneeling: `
            <circle cx="50" cy="18" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="50" y1="24" x2="50" y2="52" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="35" y1="35" x2="65" y2="35" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="52" x2="50" y2="65" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="65" x2="35" y2="80" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="50" y1="65" x2="65" y2="80" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        pigeon: `
            <circle cx="35" cy="22" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="35" y1="28" x2="40" y2="55" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="25" y1="35" x2="50" y2="38" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="40" y1="55" x2="25" y2="65" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="25" y1="65" x2="28" y2="55" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="40" y1="55" x2="75" y2="62" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
        rest: `
            <circle cx="30" cy="55" r="${HEAD_R}" fill="${STROKE}"/>
            <line x1="36" y1="55" x2="65" y2="58" stroke="${STROKE}" stroke-width="${SW}"/>
            <line x1="28" y1="50" x2="22" y2="42" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="65" y1="58" x2="72" y2="52" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
            <line x1="72" y1="52" x2="78" y2="60" stroke="${STROKE}" stroke-width="${SW}" stroke-linecap="round"/>
        `,
    };

    // Map categories and tags to SVG shape keys
    function _getShapeKey(pose) {
        const name = (pose.english_name || '').toLowerCase();
        const cat = (pose.category || '').toLowerCase();
        const tags = (pose.tags || []).map(t => t.toLowerCase());

        if (name.includes('corpse') || name.includes('savasana') || name.includes('child'))
            return 'rest';
        if (name.includes('pigeon') || name.includes('mermaid'))
            return 'pigeon';
        if (name.includes('warrior') || name.includes('lunge') || name.includes('crescent'))
            return 'lunge';
        if (name.includes('tree'))
            return 'tree';
        if (name.includes('downward') || name.includes('dolphin'))
            return 'downdog';
        if (name.includes('plank') || name.includes('chaturanga'))
            return 'plank';
        if (name.includes('forward') || name.includes('fold') || name.includes('uttanasana'))
            return 'forward_fold';
        if (name.includes('wheel') || name.includes('bow') || name.includes('cobra') ||
            name.includes('camel') || name.includes('backbend'))
            return 'backbend';
        if (name.includes('headstand') || name.includes('shoulderstand') ||
            name.includes('handstand') || name.includes('scorpion'))
            return 'inversion';
        if (name.includes('crow') || name.includes('crane') || name.includes('firefly') ||
            name.includes('flying') || name.includes('peacock') || name.includes('eight-angle'))
            return 'armbalance';
        if (tags.includes('twist'))
            return 'twist';
        if (tags.includes('balancing') || cat === 'balance')
            return 'balance';
        if (cat === 'seated')
            return 'seated';
        if (cat === 'supine')
            return 'supine';
        if (cat === 'prone')
            return 'backbend';
        if (cat === 'kneeling')
            return 'kneeling';
        if (cat === 'restorative')
            return 'rest';
        if (cat === 'core')
            return 'plank';
        if (cat === 'arm balance')
            return 'armbalance';
        if (cat === 'inversion')
            return 'inversion';
        return 'standing';
    }

    function getSVG(pose, size = 100) {
        const key = _getShapeKey(pose);
        const inner = shapes[key] || shapes.standing;
        return `<svg viewBox="0 0 100 100" width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">${inner}</svg>`;
    }

    return { getSVG };
})();
