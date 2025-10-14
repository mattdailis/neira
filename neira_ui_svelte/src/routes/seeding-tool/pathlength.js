export function pathsOfLength(length, tuples, school1, school2) {
    let frontier = [[school1, []]];
    for (let i = 0; i < length; i++) {
        let newFrontier = [];
        for (let [school, path] of frontier) {
            let visited = new Set();
            for (let tuple of path) {
                visited.add(tuple[0]);
                visited.add(tuple[1]);
            }
            for (let tuple of lookupTuples(tuples, school)) {
                let otherSchool = tuple[1]; // NOTE! Mis-nomer. It may not actually be slower, if the margin is negative
                if (visited.has(otherSchool)) {
                    continue;
                }
                newFrontier.push([otherSchool, [...path, tuple]]);
            }
        }
        frontier = newFrontier;
    }
    let paths = [];
    for (let [school, path] of frontier) {
        if (school === school2) {
            if (length === 1 || new Set(path.map(tuple => tuple[3])).size > 1) {
                paths.push(path);
            }
        }
    }
    console.log({ paths })
    return paths;
}

function lookupTuples(tuples, school) {
    let result = []
    for (const tuple of tuples) {
        if (tuple[0] === school) {
            result.push(tuple);
        } else if (tuple[1] === school) {
            result.push([tuple[1], tuple[0], -tuple[2], tuple[3], tuple[4]])
        }
    }
    return result;
}

