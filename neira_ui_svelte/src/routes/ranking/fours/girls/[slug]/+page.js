import { error } from '@sveltejs/kit';
import { parseCSV } from './csv';

export async function load({ fetch, params }) {

    const res = await fetch(`/dot/girls${params.slug}fours.csv`);
    if (res.status != 200) error(404, 'Not found');

    const table = parseCSV(await (res.text()))

    let [, ...ranking] = table[0]

    let [, ...rows] = table

    /**
     * @type Record<String, Record<String, String>>
     */
    const margins = {} // loser --> winner --> margin

    for (let school of ranking) {
        margins[school] = {}
    }

    for (let row of rows) {
        let rowSchool = row[0];
        for (let i = 1; i < row.length; i++) {
            let columnSchool = ranking[i - 1]
            let margin = row[i]
            if (margin !== "") {
                margins[rowSchool][columnSchool] = margin;
            }
        }
    }

    console.log({ margins })

    return { table, margins };
    // const item = await res.json();

    // return { item };


    // if (params.slug === 'hello-world') {
    // 	return {
    // 		title: 'Hello world!',
    // 		content: 'Welcome to our blog. Lorem ipsum dolor sit amet...'
    // 	};
    // }

    // return {
    // 	title: 'Hello world!',
    // 	content: params.slug
    // };

    // 
}