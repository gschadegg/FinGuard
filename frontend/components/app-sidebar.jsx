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
import {
  ChevronRight,
  BookOpen,
  Grid3x3,
  ChartArea,
  WalletMinimal,
  UserCircle,
  Plus,
} from 'lucide-react'
import { Button } from './ui/button'

export function AppSidebar() {
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
                  <a href="/" className="group inline-flex items-center gap-2">
                    <ChartArea className="size-5" />
                    <span>Dashboard</span>
                  </a>
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
                          <a href="/transactions">All Transactions</a>
                        </SidebarMenuButton>
                      </SidebarMenuSubItem>

                      {/* Need to make this dynamic */}

                      <SidebarMenuSubItem>
                        <SidebarMenuButton asChild>
                          <a href="#">Account 1</a>
                        </SidebarMenuButton>
                      </SidebarMenuSubItem>
                      <SidebarMenuSubItem>
                        <SidebarMenuButton asChild>
                          <a href="#">Account 2</a>
                        </SidebarMenuButton>
                      </SidebarMenuSubItem>
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
                  <a href="/budget" className="group inline-flex items-center gap-2 mb-8">
                    <BookOpen className="size-4" />
                    <span>Budget</span>
                  </a>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuSubItem>
                <SidebarMenuButton asChild>
                  <Button
                    size="sm"
                    variant="secondary"
                    asChild
                    className="bg-secondary/90 text-secondary-foreground hover:bg-primary hover:text-primary-foreground border border-border/90"
                  >
                    <Link href="#">
                      <Plus className="mr-2 size-4" />
                      Add Account
                    </Link>
                  </Button>
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
              <a href="#" className="group inline-flex items-center gap-2">
                <UserCircle className="size-5" />
                <span className="truncate">
                  Signed in as <strong>User</strong>
                </span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}
