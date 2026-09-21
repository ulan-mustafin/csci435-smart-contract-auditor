pragma solidity ^0.7.6;

contract ReentrancyVulnerable {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount);

        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent);

        balances[msg.sender] -= amount;
    }
}
