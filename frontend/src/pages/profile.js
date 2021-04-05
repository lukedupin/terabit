import React from 'react';
import { Redirect } from 'react-router-dom';
import { Button } from "react-bootstrap";
import Util from '../helpers/util';
import Web3 from 'web3';
import NftCard from "../components/nft_card";

export default class Profile extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            addresses: [],
            human: {},
            nfts: [],

            connected: false,
            resynced: false,
            loaded: false,
        };

        this.handleConnectMetaMask = this.handleConnectMetaMask.bind(this)
        this.resyncNfts = this.resyncNfts.bind(this)
    }

    componentDidMount() {
        Util.fetch_js('/human/desc/', {},
            (js) => {
                const { human, nfts, addresses } = js;
                this.setState({
                    human,
                    nfts,
                    addresses,

                    loaded: true,
                    connected: true,
                })
            },
            (reason, code) => {
                this.setState({
                    loaded: true,
                    connected: false,
                })
            })
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        const { resynced, loaded, connected, addresses } = this.state;

        //Resync!
        if ( loaded && connected && !resynced && addresses.length > 0 ) {
            this.resyncNfts( addresses[0] )
        }
    }

    resyncNfts( address ) {
        this.setState({ resynced: true })

        //Resync everything
        Util.fetch_raw("https://api.opensea.io/api/v1/assets?owner="+ address +"&limit=100")
            .then( js => {
                let clean_assets = [];

                //Load up the assests the person has
                for ( let i = 0; i < js.assets.length; i++ ) {
                    const asset = js.assets[i];
                    clean_assets.push({
                        address: asset.asset_contract.address,
                        name: asset.name,
                        desc: asset.description,
                        url: asset.external_link,
                        img: asset.image_url,
                        listing_url: asset.permalink,
                    })
                }

                //Reset the nfts
                Util.fetch_js("/nft/resync/", { 'nfts': clean_assets },
                    (js) => {
                        this.setState({ nfts: js.nfts });
                    },
                    (err, code) => {
                    });
            })
    }

    async handleConnectMetaMask() {
        const addresses = await window.ethereum.request({ method: 'eth_requestAccounts' });
        if ( addresses.length <= 0 ) {
            this.setState({err: "No account found"})
        }

        const address = addresses[0];
        console.log(address)

        const web3 = new Web3(Web3.givenProvider);

        Util.fetch_js('/human/generate_nonce/', {public_key: address}, (js) => {
            // *** WARNING
            // *** All of the code inside this warning must EXACTLY match the code in sig_valid.js, inside the server
            const msgParams = [
                {
                    type: 'string',
                    name: 'Reason',
                    value: 'Please confirm you own this account by signing the nonce. For more information: https://en.wikipedia.org/wiki/Cryptographic_nonce'  // The value to sign
                },
                {
                    type: 'string',
                    name: 'Nonce',
                    value: js.nonce
                }
            ]
            // *** WARNING

            web3.currentProvider.sendAsync({
                method: 'eth_signTypedData',
                params: [msgParams, address],
                from: address,
            }, (err, sig) => {
                console.log( sig.result );
                Util.fetch_js('/human/auth_by_nonce/', {public_key: address, signature: sig.result},
                    (js) => {
                        this.setState({
                            connected: true,

                            human: js.human,
                            addresses: js.addresses,
                            nfts: js.nfts,
                        })
                    },
                    (err, code) => {
                    });
            });
        });


    }

    render() {
        if (typeof window.ethereum === 'undefined') {
            return (<Redirect to="/" />)
        }

        const {loading, connected, resynced, human, addresses, nfts} = this.state;
        const address = (addresses.length > 0)? addresses[0]: ""

        //Loading... spinner?
        if ( loading ) {
            return (
                <div>
                    Loading profile
                </div>
            );
        }
        //Show an error
        else if ( !connected ) {
            return (
                <div>
                    <Button onClick={this.handleConnectMetaMask}>Connect MetaMask</Button>
                </div>
            );
        }
        //We have a valid profile, query the NFTs and show it
        else {
            return (
                <div>
                    <div>Name: {human.username}</div>
                    <div>Account: {address}</div>

                    <div>Nft count: {human.nft_count}</div>
                    {Object.entries(nfts).map( ([key, nft]) =>
                        <NftCard key="{key}" nft={nft}/>)}
                </div>
            );
        }
    }
}
