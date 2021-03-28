import React from 'react';

export default class Search extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            search: '',
        };

        this.handleChange = this.handleChange.bind(this);
    }

    componentDidMount() {
    }

    handleChange( event ) {
        this.setState({
            search: event.target.value,
        });

        console.log("Fetch for: "+ event.target.value )
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
