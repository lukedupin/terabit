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

                    <div className="row">
                        <div className="map-listing">
                            <div className="map-listing-head">
                                <img className="map-listing-profile" src="/static/images/user-default.png" alt="img"/>
                                <div className="map-listing-profile-deets">
                                    <a className="user-name" href="#">Richard Cranium</a>
                                    <p className="user-byline">$1,234</p>
                                </div>
                                <div className="map-listing-cta">
                                    <a className="btn" href="#">Buy</a>
                                </div>
                            </div>
                            <div className="map-listing-item">
                                <img className="map-listing-image" src="/static/images/image-location-default.jpg" alt="img"/>
                                <p className="location-latlong">43.615021, -116.202316</p>
                                <p className="location-story">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum libero sapien, mattis sed cursus non, sollicitudin vitae leo. Nullam auctor et dui sit amet ultricies. Nullam eget porttitor nisi, vel condimentum erat.</p>
                                <p className="tokens-header">Tokens</p>
                                <p className="token-title">Benny Wonderbear</p>
                                <p className="token-desc">#1821767 Gen 8</p>
                                <p className="token-title">Benny Wonderbear</p>
                                <p className="token-desc">#1821767 Gen 8</p>
                                <p className="token-title">Benny Wonderbear</p>
                                <p className="token-desc">#1821767 Gen 8</p>
                            </div>
                        </div>
                    </div>

                    <div className="row">
                        <div className="map-listing">
                            <div className="map-listing-head">
                                <img className="map-listing-profile" src="/static/images/user-default.png" alt="img"/>
                                <div className="map-listing-profile-deets">
                                    <a className="user-name" href="#">Richard Cranium</a>
                                    <p className="user-byline">$1,234</p>
                                </div>
                                <div className="map-listing-cta">
                                    <a className="btn" href="#">Buy</a>
                                </div>
                            </div>
                            <div className="map-listing-item">
                                <img className="map-listing-image" src="/static/images/image-location-default.jpg" alt="img"/>
                                <p className="location-latlong">43.615021, -116.202316</p>
                                <p className="location-story">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum libero sapien, mattis sed cursus non, sollicitudin vitae leo. Nullam auctor et dui sit amet ultricies. Nullam eget porttitor nisi, vel condimentum erat.</p>
                                <p className="tokens-header">Tokens</p>
                                <p className="token-title">Benny Wonderbear</p>
                                <p className="token-desc">#1821767 Gen 8</p>
                                <p className="token-title">Benny Wonderbear</p>
                                <p className="token-desc">#1821767 Gen 8</p>
                                <p className="token-title">Benny Wonderbear</p>
                                <p className="token-desc">#1821767 Gen 8</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}
