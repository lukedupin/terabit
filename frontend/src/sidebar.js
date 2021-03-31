import React from 'react';
import Util from './helpers/util';

import Container from 'react-bootstrap/Container';
import Button from "react-bootstrap/Button";
import NftCollection from "./nft_collection";

export default class Sidebar extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
        };

        this.linkAccount = this.linkAccount.bind(this);
    }

    linkAccount() {
        console.log("Link account");
    }

    render() {
        const { humans } = this.props;

        //We should sort the humans based on closes to center?
        const nfts = [
            { name: "Nft"},
            {name: "Nft2"}
        ];
        const human_ary =[{ username: "Test"}]// Object.entries(humans).map(([ k, h ]) => { h })

        return (
            <div className="col-lg-3">
                <div className="map-listings">
                    {Object.entries(humans).map(([k,v]) => { <NftCollection human={v} />})}
                </div>
            </div>
        );
    }
}
