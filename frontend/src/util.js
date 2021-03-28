function fetch_js( url, js ) {
    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify( js )
    };

    return fetch( url, requestOptions )
}
