import React from 'react';

export default class Contact extends React.Component {
    constructor(props) {
        super(props);

        if (typeof window.ethereum !== 'undefined') {
            console.log('MetaMask is installed!');
        }
        else {
            console.log("No meta mask here!")
        }
    }

    render() {

        return (
            <div>
                Contact page
            </div>
        );
    }
}
