import React from 'react';
import Util from './util';

export default class Search extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            search: '',
        };

        this.handleChange = this.handleChange.bind(this);
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if ( prevState.search == this.state.search ) {
            return
        }

        /*
        //Run a search
        fetch_js('/search/', this.state )
            .then( resp => resp.toJson() )
            .then( js => {
                this.props.onSearch( js )
            })
         */
    }

    handleChange( event ) {
        this.setState({
            search: event.target.value,
        });
    }

    render() {
        const { search } = this.state;
        return (
            <div className="search">
                <input
                    type="text"
                    value={search}
                    placeholder="Search"
                    onChange={this.handleChange}
                />
            </div>
        );
    }
}
