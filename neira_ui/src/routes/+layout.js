export const prerender = true;

// Import the functions you need from the SDKs you need

import { initializeApp } from "firebase/app";

import { getDatabase, ref, set, onValue } from "firebase/database";


// TODO: Add SDKs for Firebase products that you want to use

// https://firebase.google.com/docs/web/setup#available-libraries


// Your web app's Firebase configuration

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

const starCountRef = ref(db, 'users/foo');
onValue(starCountRef, (snapshot) => {
    const data = snapshot.val();
    console.log({ data })
    // updateStarCount(postElement, data);
});

/**
 * @param {any} email
 */
async function update(email) {
    await set(ref(db, 'users/foo'), { username: "abc", email })
}

console.log({ update })
