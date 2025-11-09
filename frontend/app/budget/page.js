'use client'

import React, { useMemo, useState, useEffect } from 'react'
import { useNotify } from '@/components/notification/NotificationProvider'

import PageLayout from '@/components/layouts/page-layout'
import RollupCardRow from '@/components/rollup-cards'
import { DollarSign, Plus, Calendar as CalendarIcon, Info } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  GET_BUDGET_CATEGORIES,
  CREATE_BUDGET_CATEGORY,
  UPDATE_BUDGET_CATEGORY,
  DELETE_BUDGET_CATEGORY,
} from '@/lib/api_urls'
import { useAuth } from '@/components/auth/AuthProvider'

import BudgetCategoryCard from '@/components/category-card'

import CategoryModal from '@/components/modals/CategoryModal'
import DeleteConfirmationModal from '@/components/modals/DeleteConfirmationModal'

const CATEGORY_GROUPS = ['Expenses', 'Savings', 'Entertainment']

const formatCurrency = (n) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(n)

const calcTotalBudget = (cats) =>
  CATEGORY_GROUPS.reduce(
    (sum, g) => sum + cats[g].reduce((s, c) => s + Number(c.allotted_amount ?? c.amount ?? 0), 0),
    0
  )

export default function BudgetPage() {
  const [openAdd, setOpenAdd] = useState(false)
  const [openEdit, setOpenEdit] = useState(false)
  const [openDelete, setOpenDelete] = useState(false)

  const [selectedItem, setSelectedItem] = useState({})

  const notify = useNotify()
  const { makeAuthRequest } = useAuth()

  const [totalBudget, setTotalBudget] = useState(0)
  const [categories, setCategories] = useState({
    Expenses: [],
    Savings: [],
    Entertainment: [],
  })

  const [month, _setMonth] = useState(new Date().toLocaleString('default', { month: 'long' }))

  const cardData = useMemo(() => {
    return [
      {
        title: 'Month',
        detail: month,
        icon: CalendarIcon,
      },
      {
        title: 'Total Budgeted',
        detail: `${formatCurrency(totalBudget)}`,
        icon: DollarSign,
      },
      {
        title: 'Total Spent',
        detail: '-$1,900',
        icon: DollarSign,
      },
    ]
  }, [month, totalBudget])

  useEffect(() => {
    setTotalBudget(calcTotalBudget(categories))
  }, [categories])

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const res = await makeAuthRequest(GET_BUDGET_CATEGORIES)
        if (res?.ok) {
          const { categories = [] } = res
          if (categories.length > 0) {
            const groupedData = {
              Expenses: categories.filter((c) => c.group === 'Expenses'),
              Savings: categories.filter((c) => c.group === 'Savings'),
              Entertainment: categories.filter((c) => c.group === 'Entertainment'),
            }
            setCategories(groupedData)
          }
          setTotalBudget(res?.total_budgeted)
        }
      } catch {
        notify({
          type: 'error',
          title: 'Budget Error',
          message: 'Experienced issues fetching budget categories, please try again.',
        })
      }
    }
    fetchCategories()
  }, [notify, makeAuthRequest])

  const AddCategoryBtn = (
    <Button onClick={() => setOpenAdd(true)} className="gap-2 cursor-pointer" variant="outline">
      <Plus className="h-4 w-4" /> Add Category
    </Button>
  )

  const handleCategoryEdit = (item) => {
    setSelectedItem(item)
    setOpenEdit(true)
  }

  const handleOpenDeleteModal = (item) => {
    setSelectedItem(item)
    setOpenDelete(true)
  }

  async function handleDeleteCategory(item) {
    try {
      const res = await makeAuthRequest(DELETE_BUDGET_CATEGORY(item?.id), {
        method: 'DELETE',
      })
      if (res?.ok) {
        notify({
          type: 'success',
          title: 'Category Deleted',
          message: `${item.name} category has been successfully deleted.`,
        })

        setCategories((prev) => {
          const idToDelete = item?.id
          if (!idToDelete) return prev

          return {
            Expenses: prev.Expenses.filter((c) => c.id !== idToDelete),
            Savings: prev.Savings.filter((c) => c.id !== idToDelete),
            Entertainment: prev.Entertainment.filter((c) => c.id !== idToDelete),
          }
        })
      }
      setSelectedItem({})
    } catch {
      notify({
        type: 'error',
        title: 'Error Deleting Category',
        message: 'Experienced issues deleting budget category, please try again.',
      })
    }
  }

  async function handleOnSubmitEdit(updatedItem, itemId) {
    try {
      const res = await makeAuthRequest(UPDATE_BUDGET_CATEGORY(itemId), {
        method: 'PATCH',
        body: JSON.stringify(updatedItem),
      })
      if (res?.id === itemId) {
        notify({
          type: 'success',
          title: 'Category Updated',
          message: `${updatedItem.name} category has successfully updated.`,
        })

        setCategories((prev) => {
          const base = {
            Expenses: prev.Expenses.filter((c) => c.id !== itemId),
            Savings: prev.Savings.filter((c) => c.id !== itemId),
            Entertainment: prev.Entertainment.filter((c) => c.id !== itemId),
          }
          const target = CATEGORY_GROUPS.includes(updatedItem.group)
            ? updatedItem.group
            : 'Expenses'

          return {
            ...base,
            [target]: [...base[target], { ...updatedItem, id: itemId }].sort((a, b) =>
              a.name.localeCompare(b.name)
            ),
          }
        })
      }
      setSelectedItem({})
    } catch {
      notify({
        type: 'error',
        title: 'Error Updating Category',
        message: 'Experienced issues updating budget category, please try again.',
      })
    }
  }

  async function handleOnSubmitAdd(updatedItem) {
    try {
      const res = await makeAuthRequest(CREATE_BUDGET_CATEGORY, {
        method: 'POST',
        body: JSON.stringify(updatedItem),
      })
      if (res?.id) {
        notify({
          type: 'success',
          title: 'Category Added',
          message: `${res.name} category has been successfully added.`,
        })

        setCategories((prev) => {
          const target = CATEGORY_GROUPS.includes(res.group) ? res.group : 'Expenses'
          return {
            ...prev,
            [target]: [...prev[target], res].sort((a, b) => a.name.localeCompare(b.name)),
          }
        })
      }
      setSelectedItem({})
    } catch {
      notify({
        type: 'error',
        title: 'Error Creating Category',
        message: 'Experienced issues creating budget category, please try again.',
      })
    }
  }

  return (
    <>
      <PageLayout pageTitle="Budget" action={AddCategoryBtn}>
        <RollupCardRow cardData={cardData} />
        {Object.values(categories).every((items) => !items || items.length === 0) ? (
          <p className="text-center text-gray-500 mt-8 ">
            <span className="inline-flex items-center gap-2">
              <Info className="h-4 w-4 opacity-80 " />
              You have no budget categories yet, add some!
            </span>
          </p>
        ) : (
          Object.entries(categories)
            .filter(([_groupName, items]) => items?.length > 0)
            .map(([groupName, items]) => (
              <div key={groupName}>
                <h2 className="mb-4 text-xl text-gray-500 font-semibold tracking-tight mt-8">
                  {groupName}
                </h2>
                {items.map((item) => (
                  <BudgetCategoryCard
                    key={item.id}
                    categoryId={item.id}
                    name={item.name}
                    spent={0}
                    budget={item.allotted_amount}
                    onEdit={() => handleCategoryEdit(item)}
                    onDelete={() => handleOpenDeleteModal(item)}
                  />
                ))}
              </div>
            ))
        )}
      </PageLayout>

      {/* CATEGORY MODALs */}
      {/* Add */}
      <CategoryModal
        open={openAdd}
        onOpenChange={setOpenAdd}
        mode="create"
        initial={{ name: '', group: '', amount: '' }}
        onSubmit={(payload) => {
          handleOnSubmitAdd(payload)
        }}
      />

      {/* Edit */}
      <CategoryModal
        open={openEdit}
        onOpenChange={setOpenEdit}
        mode="edit"
        initial={selectedItem}
        onSubmit={(payload, id) => {
          handleOnSubmitEdit(payload, id)
        }}
      />

      {/* Delete */}
      <DeleteConfirmationModal
        open={openDelete}
        onOpenChange={setOpenDelete}
        selectedItem={selectedItem}
        onConfirm={(item) => handleDeleteCategory(item)}
      />
    </>
  )
}
