import React from 'react';
import Util from './helpers/util';

import Container from 'react-bootstrap/Container';
import Button from "react-bootstrap/Button";

export default class Header extends React.Component {
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
        return (
            <div className="header-container">
                <Container>
                    <Button onClick={this.linkAccount}>Link Account</Button>
                    <div>Text for other stuff</div>
                </Container>
            </div>
        );
    }
}
