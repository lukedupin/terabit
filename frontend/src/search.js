import React from 'react';

export default class Search extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            search: '',
        };
    }

    componentDidMount() {
    }

    onChangeHandler( event ) {
        this.setState({
            search: event.target.value,
        });

        console.log("Fetch for: "+ this.state.search )
    }

    render() {
        return (
            <input
                type="text"
                placeholder="Search"
                onChange={this.onChangeHandler}
            />
        );
    }
}
