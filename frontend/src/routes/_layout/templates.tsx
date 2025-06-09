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
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { TemplatesService } from "../../client"

export const Route = createFileRoute("/_layout/templates")({
  component: TemplateDiscovery,
})

function TemplateDiscovery() {
  const [search, setSearch] = useState("")
  const cardBg = "white"

  const {
    data: templatesData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["templates", "discover", { search }],
    queryFn: () =>
      TemplatesService.discoverTemplates({
        skip: 0,
        limit: 20,
        search: search || undefined,
      }),
  })

  return (
    <Container maxW="7xl" py={8}>
      <VStack gap={8} alignItems="stretch">
        {/* Header */}
        <Box textAlign="center">
          <Heading size="xl" mb={4}>
            Discover Trip Templates
          </Heading>
          <Text fontSize="lg" color="gray.600" mb={6}>
            Find amazing travel experiences created by content creators
          </Text>

          {/* Search */}
          <Box maxW="md" mx="auto">
            <Input
              placeholder="Search templates..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              size="lg"
            />
          </Box>
        </Box>

        {/* Templates Grid */}
        {isLoading ? (
          <Text textAlign="center">Loading templates...</Text>
        ) : error ? (
          <Box textAlign="center" py={8}>
            <Text color="red.500" mb={4}>
              Failed to load templates
            </Text>
            <Button onClick={() => window.location.reload()}>Try Again</Button>
          </Box>
        ) : templatesData?.data?.length === 0 ? (
          <Box textAlign="center" py={12}>
            <Text fontSize="6xl" mb={4}>
              🗺️
            </Text>
            <Heading size="md" mb={2}>
              No templates found
            </Heading>
            <Text color="gray.600">
              {search
                ? "Try adjusting your search terms"
                : "No templates available yet"}
            </Text>
          </Box>
        ) : (
          <Grid templateColumns="repeat(auto-fill, minmax(350px, 1fr))" gap={6}>
            {templatesData?.data?.map((template) => (
              <Box
                key={template.id}
                p={6}
                bg={cardBg}
                borderRadius="md"
                borderWidth={1}
                _hover={{ transform: "translateY(-2px)", shadow: "lg" }}
              >
                <VStack alignItems="stretch" gap={4}>
                  {/* Template Header */}
                  <Box>
                    <HStack justify="space-between" mb={2}>
                      <Badge colorScheme="green">Published</Badge>
                      <Text fontSize="sm" color="gray.600">
                        {template.views_count} views
                      </Text>
                    </HStack>
                    <Heading size="md" mb={2}>
                      {template.title}
                    </Heading>
                    <Text color="gray.600" lineClamp={3}>
                      {template.description}
                    </Text>
                  </Box>

                  {/* Creator Info */}
                  {template.creator && (
                    <HStack>
                      <Box w={8} h={8} bg="gray.200" borderRadius="full" />
                      <VStack alignItems="start" gap={0}>
                        <Text fontSize="sm" fontWeight="medium">
                          {template.creator.display_name}
                        </Text>
                        <Text fontSize="xs" color="gray.600">
                          @{template.creator.username}
                        </Text>
                      </VStack>
                    </HStack>
                  )}

                  {/* Core Experience Preview */}
                  <Box>
                    <Text fontSize="sm" fontWeight="medium" mb={2}>
                      Core Experience:
                    </Text>
                    <Stack direction="row" wrap="wrap" gap={1}>
                      {Object.keys(template.core_experience || {})
                        .slice(0, 3)
                        .map((key) => (
                          <Badge key={key} variant="outline" size="sm">
                            {key.replace(/_/g, " ").toUpperCase()}
                          </Badge>
                        ))}
                      {Object.keys(template.core_experience || {}).length >
                        3 && (
                        <Badge variant="outline" size="sm" color="gray.500">
                          +
                          {Object.keys(template.core_experience || {}).length -
                            3}{" "}
                          more
                        </Badge>
                      )}
                    </Stack>
                  </Box>

                  {/* Actions */}
                  <HStack gap={2}>
                    <Button colorScheme="blue" flex={1}>
                      View Details
                    </Button>
                    <Button variant="outline" flex={1}>
                      Customize
                    </Button>
                  </HStack>
                </VStack>
              </Box>
            ))}
          </Grid>
        )}

        {/* Stats */}
        {templatesData && (
          <Box textAlign="center" pt={8}>
            <Text color="gray.600">
              Showing {templatesData.data.length} of {templatesData.count}{" "}
              templates
            </Text>
          </Box>
        )}
      </VStack>
    </Container>
  )
}
