//go:build !windows

package main
import "net"
func localGateways() []net.IP{return nil}
