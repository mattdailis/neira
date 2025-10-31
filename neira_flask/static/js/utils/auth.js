let auth0Client = null;
const fetchAuthConfig = () => fetch("/static/auth_config.json");

export async function login() {
    await auth0Client.loginWithRedirect({
        authorizationParams: {
            redirect_uri: window.location.origin,
            scope: 'curate'
        }
    });
};

const configureClient = async () => {
    const response = await fetchAuthConfig();
    const config = await response.json();

    auth0Client = await auth0.createAuth0Client({
        domain: config.domain,
        clientId: config.clientId,
        cacheLocation: 'localstorage',
        authorizationParams: {
          audience: 'https://neiraseeding.org/api'
        }
    });
};

window.onload = async () => {
    console.log("Calling configureClient")
    await configureClient();
    const isAuthenticated = await auth0Client.isAuthenticated();
    console.log("isAuthenticated", isAuthenticated);

    if (isAuthenticated) {
        updateUI();
        // show the gated content
        return;
    }

    // NEW - check for the code and state parameters
    const query = window.location.search;
    if (query.includes("code=") && query.includes("state=")) {

        // Process the login state
        await auth0Client.handleRedirectCallback();

        updateUI();

        // Use replaceState to redirect the user away and remove the querystring parameters
        window.history.replaceState({}, document.title, "/");
    }
};

export async function logout() {
    auth0Client.logout({
        logoutParams: {
            returnTo: window.location.origin
        }
    });
};

const updateUI = async () => {
    // const isAuthenticated = await auth0Client.isAuthenticated();
    
};

export async function foo() {
    const accessToken = await auth0Client.getTokenSilently();
    const result = await fetch('/api/test', {
        method: 'GET',
        headers: {
            Authorization: 'Bearer ' + accessToken
        }
    });
    const data = await result.json();
    console.log(data);
}