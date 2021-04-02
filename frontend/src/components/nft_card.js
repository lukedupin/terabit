import React from 'react';

import Container from 'react-bootstrap/Container';
import Button from "react-bootstrap/Button";

import Util from '../helpers/util';

export default class NftCard extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const { nft } = this.props;

        return (
            <div className="map-listing-item">
                <img className="map-listing-image" src="/static/images/image-location-default.jpg" alt="img"/>
                <p className="location-latlong">43.615021, -116.202316</p>
                <p className="location-story">{nft.desc}</p>
                <p className="tokens-header">{nft.name}</p>
                <p className="token-title">{nft.url}</p>
                <p className="token-desc"></p>
            </div>
        );
    }
}
