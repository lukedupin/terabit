import React from 'react';

import Container from 'react-bootstrap/Container';
import Button from "react-bootstrap/Button";

import NftCollection from "./nft_collection";
import Util from '../helpers/util';

export default class Sidebar extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            human_nfts: {},
            update_id: 0,
        };

        this.linkAccount = this.linkAccount.bind(this);
    }

    linkAccount() {
        console.log("Link account");
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        const update_id = this.state.update_id;

        //If state changed, do nothing, we only care about props
        if ( prevState.update_id != update_id ) {
            return;
        }

        //Update!
        const human_uids = Object.entries(this.props.humans).map(([k,v]) => k);
        Util.fetch_js("/nft/bulk_list/", { human_uids }, ( js ) => {
            const {humans} = this.props;

            //Initially populate the human part into the nfts
            let human_nfts = {};
            for (let i = 0; i < human_uids.length; i++) {
                const key = human_uids[i];
                human_nfts[key] = {
                    ...this.props.humans[key],
                    nfts: []
                };
            }

            //Build out my nfts based on human_uids
            for (let i = 0; i < js.nfts.length; i++) {
                const nft = js.nfts[i];
                if (nft.human_uid in human_nfts) {
                    human_nfts[nft.human_uid].nfts.push(nft);
                }
            }

            //Finally convert this object into an array
            this.setState({
                human_nfts: Object.entries(human_nfts).map(([k, v]) => v),
                update_id: update_id + 1, //This prevents the Update call that happens from hitting the server again
            })
        })
    }

    render() {
        const { human_nfts } = this.state;

        return (
            <div className="col-lg-3">
                <div className="map-listings">
                    {Object.entries(human_nfts).map(([k,v]) => <NftCollection human={v} />)}
                </div>
            </div>
        );
    }
}
