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
                let owner = null;
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

                    //Store the image
                    if ( 'owner' in asset && 'user' in asset.owner ) {
                        owner = {
                            username:       asset.owner.user.username,
                            profile_image:  asset.owner.profile_img_url,
                        }
                    }
                }

                //Reset the nfts
                Util.fetch_js("/nft/resync/", { 'nfts': clean_assets },
                    (js) => {
                        this.setState({
                            human: js.human,
                            nfts: js.nfts,
                        });
                    },
                    (err, code) => {
                    });

                //Update teh user?
                if ( owner != null ) {
                    Util.fetch_js("/human/soft_modify/", owner,
                        (human) => {
                            this.setState({human});
                        },
                        (err, code) => {
                        });
                }
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

        const {loading, connected, addresses, nfts} = this.state;
        //const address = (addresses.length > 0)? addresses[0]: ""

        //Pull the human but set a default
        let { human } = this.state;
        if ( !('username' in human) ) {
            human = {
                username: 'Terabit profile',
                profile_image: '/static/images/user-default.png',
                bio: 'Bio',
            };
        }

        //User needs to connect Meta mask
        const conn_str = ( connected )? "Reconnect MetaMask": "Connect MetaMask";

        //Loading... spinner?
        if ( loading ) {
            return (
                <div>
                    Loading profile
                </div>
            );
        }

        return (
            <section className="app-body">

                <div className="container-fluid">
                    <div className="row">
                        <div className="col-lg-3">
                            <div className="myprofile">
                                <img className="myprofile-image" src={human.profile_image} alt="img"/>
                                <p className="myprofile-name">{human.username}</p>
                                <a className="btn btn-ghost" href="#" onClick={this.handleConnectMetaMask}>{conn_str}</a>
                                <a className="link-color" href="#"></a>
                                <hr/>
                                <p className="myprofile-bio">{human.bio}</p>
                            </div>
                        </div>

                        <div className="col-lg-9">
                            <div className="row">

                                {Object.entries(nfts).map( ([key, nft]) =>
                                    <div className="nft-card" key="{key}">
                                        <img className="nft-card-image" src={nft.img} alt="img"/>
                                        <p className="nft-name">{nft.name}</p>
                                        <p className="nft-desc">{nft.desc}</p>
                                        <a target="_blank" rel="noopener noreferrer" href={nft.url}>Link</a>
                                        <a target="_blank" rel="noopener noreferrer" href={nft.listing_url}>Buy</a>
                                    </div>
                                )}

                            </div>
                        </div>
                    </div>
                </div>

            </section>
        );
    }
}
