// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/// @title USSToken - базовый токен для стейкинга
contract USSToken is ERC20, Ownable {
    event Minted(address indexed to, uint256 amount);
    event Burned(address indexed from, uint256 amount);

    constructor() ERC20("USS Token", "USS") Ownable(msg.sender) {}

    /// @notice Минт новых токенов (только владелец)
    function mint(address to, uint256 amount) external onlyOwner {
        require(amount > 0, "Mint amount must be > 0");
        _mint(to, amount);
        emit Minted(to, amount);
    }

    /// @notice Сжечь токены у себя
    function burn(uint256 amount) external {
        require(amount > 0, "Burn amount must be > 0");
        _burn(msg.sender, amount);
        emit Burned(msg.sender, amount);
    }

    /// @notice Сжечь токены у другого адреса (если есть allowance)
    function burnFrom(address from, uint256 amount) external {
        require(amount > 0, "Burn amount must be > 0");
        uint256 currentAllowance = allowance(from, msg.sender);
        require(currentAllowance >= amount, "Burn amount exceeds allowance");
        _approve(from, msg.sender, currentAllowance - amount);
        _burn(from, amount);
        emit Burned(from, amount);
    }
}

