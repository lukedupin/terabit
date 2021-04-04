import React from 'react';
import { Button } from "react-bootstrap";
import Util from '../helpers/util';
import web3 from 'web3';

export default class Profile extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            err: "",
            account: "",
        };

        this.handleConnectMetaMask = this.handleConnectMetaMask.bind(this)
    }

    async handleConnectMetaMask() {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        if ( accounts.length <= 0 ) {
            this.setState({err: "No account found"})
        }

        /*
        const account = accounts[0];
        console.log(account)

        Util.fetch_js('/human/generate_nonce/', {public_key: account}, (js) => {
            console.log(js.nonce);
            console.log( window.web3 );
            web3.personal.sign( js.nonce, account, (err, sig) => {
                console.log( sig );
            });
        });
         */

        const address = "0xFe5B4b73Fd25dD1b0692266c5cD105E61721BE65";
        Util.fetch_raw("https://api.opensea.io/api/v1/assets?owner="+ address +"&limit=20")
            .then( js => {
                for ( let i = 0; i < js.assets.length; i++ ) {
                    const asset = js.assets[i];
                    Util.fetch_js("/nft/create/", {
                        human_uid: "00",
                        address: asset.asset_contract.address,
                        name: asset.name,
                        desc: asset.description,
                        url: asset.external_link,
                        img: asset.image_url,
                        listing_url: asset.permalink,
                    },
                    js => {
                        console.log("Saved")
                    })
                }
            })
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
