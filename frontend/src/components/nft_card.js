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
            <div className="header-container">
                {nft.name}
            </div>
        );
    }
}
