'use client'
import * as React from 'react'
import Link from 'next/link'
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarMenuSub,
  SidebarMenuSubItem,
  SidebarHeader,
  SidebarFooter,
} from '@/components/ui/sidebar'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'

import { Skeleton } from './ui/skeleton'
import { ChevronRight, BookOpen, Grid3x3, ChartArea, WalletMinimal, UserCircle } from 'lucide-react'
import { useUserContext } from './user-data'
import { CreateLinkAccountButton } from '@/components/create-plaid-connection'

export function AppSidebar() {
  const { accounts, userId } = useUserContext()

  return (
    <Sidebar>
      <SidebarHeader className="px-4 py-6 mb-3 flex justify-between border-b border-border">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <Grid3x3 className="size-6" />
            <div className="text-base font-semibold leading-tight">FinGuard</div>
          </div>
          <div className="pl-8 text-xs text-muted-foreground">protecting transactions.</div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/" className="group inline-flex items-center gap-2">
                    <ChartArea className="size-5" />
                    <span>Dashboard</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Accounts*/}
        <SidebarGroup>
          <SidebarGroupContent>
            <Collapsible defaultOpen className="group/collapsible">
              <SidebarMenu>
                <SidebarMenuItem>
                  <CollapsibleTrigger asChild>
                    <SidebarMenuButton>
                      <WalletMinimal className="size-4" />
                      <span>Accounts</span>
                      <ChevronRight className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-90" />
                    </SidebarMenuButton>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <SidebarMenuSub>
                      <SidebarMenuSubItem>
                        <SidebarMenuButton asChild>
                          <Link href="/accounts">All Accounts</Link>
                        </SidebarMenuButton>
                      </SidebarMenuSubItem>

                      {accounts ? (
                        accounts.length > 0 ? (
                          accounts.map((account) => (
                            <SidebarMenuSubItem key={account.id}>
                              <SidebarMenuButton asChild>
                                <Link href={`/accounts/${account.id}`}>
                                  {account.institution_name} - {account.name}
                                </Link>
                              </SidebarMenuButton>
                            </SidebarMenuSubItem>
                          ))
                        ) : (
                          <SidebarMenuSubItem>No Linked Accounts</SidebarMenuSubItem>
                        )
                      ) : (
                        <SidebarMenuSubItem>
                          <SidebarMenuButton asChild>
                            <Skeleton />
                          </SidebarMenuButton>
                        </SidebarMenuSubItem>
                      )}
                    </SidebarMenuSub>
                  </CollapsibleContent>
                </SidebarMenuItem>
              </SidebarMenu>
            </Collapsible>
          </SidebarGroupContent>
        </SidebarGroup>
        {/* Budget */}
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/budget" className="group inline-flex items-center gap-2 mb-8">
                    <BookOpen className="size-4" />
                    <span>Budget</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuSubItem>
                <SidebarMenuButton asChild>
                  <CreateLinkAccountButton userId={userId} />
                </SidebarMenuButton>
              </SidebarMenuSubItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      {/* Footer Area */}
      <SidebarFooter className="p-3 mt-auto">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="#" className="group inline-flex items-center gap-2">
                <UserCircle className="size-5" />
                <span className="truncate">
                  Signed in as <strong>User</strong>
                </span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}
