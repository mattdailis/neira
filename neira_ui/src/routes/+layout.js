export const prerender = true;

// Import the functions you need from the SDKs you need

import { initializeApp } from "firebase/app";

import { getDatabase, ref, set, onValue } from "firebase/database";


// TODO: Add SDKs for Firebase products that you want to use

// https://firebase.google.com/docs/web/setup#available-libraries


export async function load({ params }) {
    const firebaseConfig = {
        apiKey: "AIzaSyC4wR7v4I0iMKzy_h_BjQ-RGgJrJV7knsc",
        authDomain: "neira-f9621.firebaseapp.com",
        databaseURL: "https://neira-f9621.firebaseio.com",
        projectId: "neira-f9621",
        storageBucket: "neira-f9621.appspot.com",
        messagingSenderId: "107972862685",
        appId: "1:107972862685:web:58b89d4c93648c3bc63134"
    };


    // Initialize Firebase

    const app = initializeApp(firebaseConfig);


    const db = getDatabase(app);

    console.log({ db, ref, set })

    // const starCountRef = ref(db, 'users/foo');
    // const unsubscribe = onValue(starCountRef, (snapshot) => {
    //     const data = snapshot.val();
    //     console.log({ data })
    //     unsubscribe();
    //     // updateStarCount(postElement, data);
    // });

    /**
     * @param {any} email
     */
    async function update(email) {
        await set(ref(db, 'users/foo'), { username: "abc", email })
    }

    console.log({ update })

    const racesRef = ref(db, 'races');
    const foundersDayRef = ref(db, 'founders-day/2024');

    const promises = await Promise.all([new Promise(resolve => {
        const unsubscribe = onValue(racesRef, snapshot => {
            const newRaces = snapshot.val()
            unsubscribe();
            resolve({ races: newRaces })
        });
    }), new Promise(resolve => {
        const unsubscribe = onValue(foundersDayRef, snapshot => {
            const race = snapshot.val()

            const tuples = [];

            for (const entry of race.head_to_head) {
                if (entry.results === undefined) continue;
                for (const result of entry.results) {
                    if (entry.class === 'fours' && entry.gender === 'girls' && entry.varsity_index === '1') {
                        tuples.push([result.school1, result.school2, result.margin, race.day, race.url])
                    }
                }
            }
            unsubscribe();
            resolve({ foundersDay: tuples })
        });
    })])

    return {
        races: promises[0].races,
        foundersDay: promises[1].foundersDay,
    }
}
// Your web app's Firebase configuration

