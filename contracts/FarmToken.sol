// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/// @title FarmToken — ERC20 токен наград для стейкинга
/// @notice Только staking-контракт может минтить (через transferOwnership)
contract FarmToken is ERC20, Ownable {
    event Minted(address indexed to, uint256 amount);
    event Burned(address indexed from, uint256 amount);

    constructor() ERC20("Farm Token", "FARM") Ownable(msg.sender) {
        // ⚠ Нет начального минта: токены выдаются за активность
    }

    /// @notice Минт новых токенов (например, из staking контракта)
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
        emit Minted(to, amount);
    }

    /// @notice Сжечь токены у себя
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
        emit Burned(msg.sender, amount);
    }

    /// @notice Сжечь с другого адреса по allowance
    function burnFrom(address from, uint256 amount) external {
        uint256 currentAllowance = allowance(from, msg.sender);
        require(currentAllowance >= amount, "ERC20: burn amount exceeds allowance");
        _approve(from, msg.sender, currentAllowance - amount);
        _burn(from, amount);
        emit Burned(from, amount);
    }
}

