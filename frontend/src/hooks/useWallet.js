import { createConfig, http, useAccount, useConnect, useDisconnect } from 'wagmi'
import { bsc } from 'wagmi/chains'
import { injected } from 'wagmi/connectors'

export const wagmiConfig = createConfig({
  chains: [bsc],
  connectors: [injected()],
  transports: {
    [bsc.id]: http('https://bsc-dataseed1.binance.org'),
  },
})

export function useWallet() {
  const { address, isConnected, chain } = useAccount()
  const { connect, connectors } = useConnect()
  const { disconnect } = useDisconnect()

  const connectWallet = () => {
    const connector = connectors[0]
    if (connector) {
      connect({ connector })
    }
  }

  return {
    address,
    isConnected,
    chain,
    connect: connectWallet,
    disconnect,
    connectors,
  }
}
