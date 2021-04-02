import React from 'react';
import { Button } from "react-bootstrap";

export default class Profile extends React.Component {
    constructor(props) {
        super(props);

        this.handleConnectMetaMask = this.handleConnectMetaMask.bind(this)
    }

    async handleConnectMetaMask() {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        for ( let i = 0; i < accounts.length; i++ ) {
            const account = accounts[i];
            console.log(account)
        }
    }

    render() {
        if (typeof window.ethereum === 'undefined') {
            return (<Redirect to="/" />)
        }

        return (
            <div>
                <Button onClick={this.handleConnectMetaMask}>Connect MetaMask</Button>
                Profile
            </div>
        );
    }
}
