import React from 'react';

import Container from 'react-bootstrap/Container';
import Button from "react-bootstrap/Button";

import Util from '../helpers/util';

export default class NftLandCard extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const { nft } = this.props;

        return (
            <div className="map-listing-item">
                <div className="map-listing-cta">
                    <a className="btn" target="_blank" rel="noopener noreferrer" href={nft.listing_url}>Buy</a>
                </div>
                <img className="map-listing-image" src={nft.img} alt="img"/>
                <p className="location-story"></p>
                <p className="tokens-header">Tokens</p>
                <p class="token-title">{nft.name}</p>
                <p className="token-desc">{nft.desc}</p>
                <a className="link-color" target="_blank" rel="noopener noreferrer" href={nft.url}>Link</a>
            </div>
        );
    }
}
