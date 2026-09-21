pragma solidity ^0.7.6;

contract IntegerOverflowVulnerable {
    uint256 public total;

    function add(uint256 amount) external {
        total += amount;
    }
}
