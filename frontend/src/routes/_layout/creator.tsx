import {
  Badge,
  Box,
  Button,
  Container,
  Grid,
  HStack,
  Heading,
  Input,
  Stack,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { CreatorsService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

export const Route = createFileRoute("/_layout/creator")({
  component: CreatorDashboard,
})

function CreatorDashboard() {
  const bgColor = "gray.50"
  const cardBg = "white"
  const [showTemplateForm, setShowTemplateForm] = useState(false)
  const [templateFormData, setTemplateFormData] = useState({
    title: "",
    description: "",
    creator_notes: "",
    core_experience: {},
    flexible_logistics: {},
  })

  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  // Query creator profile
  const {
    data: creator,
    isLoading: creatorLoading,
    error: creatorError,
  } = useQuery({
    queryKey: ["creator", "profile"],
    queryFn: CreatorsService.getMyCreatorProfile,
    retry: false,
  })

  // Query creator templates
  const { data: templatesData, isLoading: templatesLoading } = useQuery({
    queryKey: ["creator", "templates"],
    queryFn: () => CreatorsService.getMyTemplates({ skip: 0, limit: 10 }),
    enabled: !!creator,
  })

  // Create template mutation
  const createTemplateMutation = useMutation({
    mutationFn: (data: typeof templateFormData) =>
      CreatorsService.createTripTemplate({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Template created successfully")
      queryClient.invalidateQueries({ queryKey: ["creator", "templates"] })
      setShowTemplateForm(false)
      setTemplateFormData({
        title: "",
        description: "",
        creator_notes: "",
        core_experience: {},
        flexible_logistics: {},
      })
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to create template")
    },
  })

  const handleTemplateSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!templateFormData.title || !templateFormData.description) {
      showErrorToast("Please fill in all required fields")
      return
    }
    
    // Set some basic default values for core_experience and flexible_logistics
    const templateData = {
      ...templateFormData,
      core_experience: templateFormData.core_experience || { destination: templateFormData.title },
      flexible_logistics: templateFormData.flexible_logistics || { duration: "7 days" },
    }
    
    createTemplateMutation.mutate(templateData)
  }

  if (creatorLoading) {
    return (
      <Container maxW="7xl" py={8}>
        <Text>Loading...</Text>
      </Container>
    )
  }

  // Show creator setup if no creator profile
  if (creatorError || !creator) {
    return <CreatorSetup />
  }

  // Show template creation form
  if (showTemplateForm) {
    return <TemplateCreationForm 
      formData={templateFormData}
      setFormData={setTemplateFormData}
      onSubmit={handleTemplateSubmit}
      onCancel={() => setShowTemplateForm(false)}
      isLoading={createTemplateMutation.isPending}
    />
  }

  return (
    <Container maxW="7xl" py={8} bg={bgColor} minH="100vh">
      <VStack gap={8} alignItems="stretch">
        {/* Header */}
        <Box>
          <HStack justify="space-between" align="start">
            <VStack alignItems="start" gap={2}>
              <Heading size="xl">Creator Dashboard</Heading>
              <HStack>
                <Text color="gray.600">
                  Welcome back, {creator.display_name}
                </Text>
                <Badge
                  colorScheme={creator.status === "active" ? "green" : "yellow"}
                >
                  {creator.status}
                </Badge>
              </HStack>
            </VStack>
            <Button 
              colorScheme="blue" 
              size="lg"
              onClick={() => setShowTemplateForm(true)}
            >
              Create New Template
            </Button>
          </HStack>
        </Box>

        {/* Stats Cards */}
        <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6}>
          <Box p={6} bg={cardBg} borderRadius="md" borderWidth={1}>
            <VStack alignItems="start">
              <Text fontSize="sm" color="gray.600" fontWeight="medium">
                Total Templates
              </Text>
              <Text fontSize="3xl" fontWeight="bold">
                {templatesData?.count || 0}
              </Text>
            </VStack>
          </Box>

          <Box p={6} bg={cardBg} borderRadius="md" borderWidth={1}>
            <VStack alignItems="start">
              <Text fontSize="sm" color="gray.600" fontWeight="medium">
                Published
              </Text>
              <Text fontSize="3xl" fontWeight="bold">
                {templatesData?.data?.filter((t) => t.status === "published")
                  .length || 0}
              </Text>
            </VStack>
          </Box>

          <Box p={6} bg={cardBg} borderRadius="md" borderWidth={1}>
            <VStack alignItems="start">
              <Text fontSize="sm" color="gray.600" fontWeight="medium">
                Total Views
              </Text>
              <Text fontSize="3xl" fontWeight="bold">
                {templatesData?.data?.reduce(
                  (sum, t) => sum + (t.views_count || 0),
                  0,
                ) || 0}
              </Text>
            </VStack>
          </Box>

          <Box p={6} bg={cardBg} borderRadius="md" borderWidth={1}>
            <VStack alignItems="start">
              <Text fontSize="sm" color="gray.600" fontWeight="medium">
                Commission Rate
              </Text>
              <Text fontSize="3xl" fontWeight="bold">
                {Math.round((creator.commission_rate || 0) * 100)}%
              </Text>
            </VStack>
          </Box>
        </Grid>

        {/* Recent Templates */}
        <Box p={6} bg={cardBg} borderRadius="md" borderWidth={1}>
          <VStack alignItems="stretch" gap={4}>
            <HStack justify="space-between">
              <Heading size="md">Recent Templates</Heading>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => showSuccessToast("View All feature coming soon!")}
              >
                View All
              </Button>
            </HStack>

            {templatesLoading ? (
              <Text>Loading templates...</Text>
            ) : templatesData?.data?.length === 0 ? (
              <Box textAlign="center" py={8}>
                <Text color="gray.600" mb={4}>
                  You haven't created any templates yet.
                </Text>
                <Button 
                  colorScheme="blue"
                  onClick={() => setShowTemplateForm(true)}
                >
                  Create Your First Template
                </Button>
              </Box>
            ) : (
              <Stack gap={3}>
                {templatesData?.data?.slice(0, 5).map((template) => (
                  <Box
                    key={template.id}
                    p={4}
                    border="1px"
                    borderColor="gray.200"
                    borderRadius="md"
                    _hover={{ borderColor: "blue.300" }}
                  >
                    <HStack justify="space-between">
                      <VStack alignItems="start" gap={1}>
                        <Text fontWeight="medium">{template.title}</Text>
                        <HStack gap={4}>
                          <Badge
                            colorScheme={
                              template.status === "published" ? "green" : "gray"
                            }
                          >
                            {template.status}
                          </Badge>
                          <Text fontSize="sm" color="gray.600">
                            {template.views_count} views
                          </Text>
                          <Text fontSize="sm" color="gray.600">
                            Created{" "}
                            {new Date(template.created_at).toLocaleDateString()}
                          </Text>
                        </HStack>
                      </VStack>
                      <HStack>
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={() => showSuccessToast("Edit feature coming soon!")}
                        >
                          Edit
                        </Button>
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={() => showSuccessToast("Share feature coming soon!")}
                        >
                          Share
                        </Button>
                      </HStack>
                    </HStack>
                  </Box>
                ))}
              </Stack>
            )}
          </VStack>
        </Box>
      </VStack>
    </Container>
  )
}

function CreatorSetup() {
  const cardBg = "white"
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    username: "",
    display_name: "",
    bio: "",
  })
  
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const createCreatorMutation = useMutation({
    mutationFn: (data: typeof formData) => 
      CreatorsService.createCreatorProfile({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Creator profile created successfully")
      queryClient.invalidateQueries({ queryKey: ["creator", "profile"] })
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to create creator profile")
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.username || !formData.display_name) {
      showErrorToast("Please fill in all required fields")
      return
    }
    createCreatorMutation.mutate(formData)
  }

  if (showForm) {
    return (
      <Container maxW="2xl" py={12}>
        <Box p={8} bg={cardBg} borderRadius="md" borderWidth={1}>
          <VStack gap={6}>
            <Box textAlign="center">
              <Heading size="lg" mb={2}>
                Create Your Creator Profile
              </Heading>
              <Text color="gray.600">
                Tell us about yourself and start your creator journey
              </Text>
            </Box>

            <form onSubmit={handleSubmit} style={{ width: "100%" }}>
              <VStack gap={4} w="full">
                <Box w="full">
                  <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Username *
                  </Text>
                  <Input
                    placeholder="@yourhandle"
                    value={formData.username}
                    onChange={(e) =>
                      setFormData({ ...formData, username: e.target.value })
                    }
                  />
                </Box>

                <Box w="full">
                  <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Display Name *
                  </Text>
                  <Input
                    placeholder="Your Full Name"
                    value={formData.display_name}
                    onChange={(e) =>
                      setFormData({ ...formData, display_name: e.target.value })
                    }
                  />
                </Box>

                <Box w="full">
                  <Text fontSize="sm" fontWeight="medium" mb={2}>
                    Bio
                  </Text>
                  <Textarea
                    placeholder="Tell your audience about your travel experiences..."
                    value={formData.bio}
                    onChange={(e) =>
                      setFormData({ ...formData, bio: e.target.value })
                    }
                    rows={4}
                  />
                </Box>

                <HStack w="full" gap={4}>
                  <Button
                    variant="outline"
                    flex={1}
                    onClick={() => setShowForm(false)}
                    disabled={createCreatorMutation.isPending}
                  >
                    Back
                  </Button>
                  <Button
                    type="submit"
                    colorScheme="blue"
                    flex={1}
                    loading={createCreatorMutation.isPending}
                  >
                    {createCreatorMutation.isPending ? "Creating..." : "Create Profile"}
                  </Button>
                </HStack>
              </VStack>
            </form>
          </VStack>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxW="2xl" py={12}>
      <Box p={8} bg={cardBg} textAlign="center" borderRadius="md" borderWidth={1}>
        <VStack gap={6}>
          <Box>
            <Text fontSize="6xl" mb={4}>
              🎯
            </Text>
            <Heading size="lg" mb={2}>
              Become a Creator
            </Heading>
            <Text color="gray.600">
              Start monetizing your travel experiences by creating trip
              templates that your followers can book and customize.
            </Text>
          </Box>

          <VStack gap={4} w="full">
            <Box>
              <Text fontWeight="medium" mb={2}>
                What you can do:
              </Text>
              <VStack alignItems="start" gap={2}>
                <Text fontSize="sm">
                  ✈️ Create trip templates with your experiences
                </Text>
                <Text fontSize="sm">
                  🔗 Generate affiliate links for sharing
                </Text>
                <Text fontSize="sm">📊 Track performance and earnings</Text>
                <Text fontSize="sm">💰 Earn commissions on bookings</Text>
              </VStack>
            </Box>

            <Button 
              colorScheme="blue" 
              size="lg" 
              w="full"
              onClick={() => setShowForm(true)}
            >
              Set Up Creator Profile
            </Button>
          </VStack>
        </VStack>
      </Box>
    </Container>
  )
}

interface TemplateCreationFormProps {
  formData: {
    title: string
    description: string
    creator_notes: string
    core_experience: any
    flexible_logistics: any
  }
  setFormData: (data: any) => void
  onSubmit: (e: React.FormEvent) => void
  onCancel: () => void
  isLoading: boolean
}

function TemplateCreationForm({ 
  formData, 
  setFormData, 
  onSubmit, 
  onCancel, 
  isLoading 
}: TemplateCreationFormProps) {
  const cardBg = "white"

  return (
    <Container maxW="4xl" py={12}>
      <Box p={8} bg={cardBg} borderRadius="md" borderWidth={1}>
        <VStack gap={6}>
          <Box textAlign="center">
            <Heading size="lg" mb={2}>
              Create Trip Template
            </Heading>
            <Text color="gray.600">
              Share your travel experience and help others plan amazing trips
            </Text>
          </Box>

          <form onSubmit={onSubmit} style={{ width: "100%" }}>
            <VStack gap={6} w="full">
              <Box w="full">
                <Text fontSize="sm" fontWeight="medium" mb={2}>
                  Template Title *
                </Text>
                <Input
                  placeholder="e.g., 7-Day Tokyo Adventure"
                  value={formData.title}
                  onChange={(e) =>
                    setFormData({ ...formData, title: e.target.value })
                  }
                />
              </Box>

              <Box w="full">
                <Text fontSize="sm" fontWeight="medium" mb={2}>
                  Description *
                </Text>
                <Textarea
                  placeholder="Describe what makes this trip special and what travelers can expect..."
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  rows={4}
                />
              </Box>

              <Box w="full">
                <Text fontSize="sm" fontWeight="medium" mb={2}>
                  Creator Notes
                </Text>
                <Textarea
                  placeholder="Share insider tips, personal recommendations, or important notes for travelers..."
                  value={formData.creator_notes}
                  onChange={(e) =>
                    setFormData({ ...formData, creator_notes: e.target.value })
                  }
                  rows={3}
                />
              </Box>

              <HStack w="full" gap={4}>
                <Button
                  variant="outline"
                  flex={1}
                  onClick={onCancel}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  colorScheme="blue"
                  flex={1}
                  loading={isLoading}
                >
                  {isLoading ? "Creating..." : "Create Template"}
                </Button>
              </HStack>
            </VStack>
          </form>
        </VStack>
      </Box>
    </Container>
  )
}
