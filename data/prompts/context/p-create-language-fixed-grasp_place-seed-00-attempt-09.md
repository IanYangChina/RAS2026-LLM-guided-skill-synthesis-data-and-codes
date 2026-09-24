## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.1181 | 0.32 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2618 | 0.32 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0590 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1378 | 0.24 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0352 | 0.18 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.118) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: grasp_1
- id: lift_transport
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_retention
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: transport_arc
- id: place_approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: release_1
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_transport** (`lift`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_retention, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=reduce_speed
- **place_approach** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.118
- **task_score** (E): 0.318
- **fitness_score**: 0.382  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0766 |
| descend_1 | 1.00 | 1.00 | 0.1997 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_up | 0.00 | 1.00 | 0.0001 |
| transport | 0.00 | 1.00 | 0.1802 |
| descend_release | 1.00 | 1.00 | 0.0790 |
| release_gripper | 1.00 | 1.00 | 0.0220 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.000, 0.245) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.495, -0.000, 0.245)→(0.492, 0.001, 0.046) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.046)→(0.484, 0.000, 0.037) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 44.333 | 0.142 | 0.194 |
| lift_up | lift | 0.00 / guard_failure | (0.484, 0.000, 0.037)→(0.484, 0.000, 0.037) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.266→0.266 | 1.00 / 44.333 | 0.258 | 0.258 |
| transport | approach | 0.00 / step_budget | (0.484, 0.000, 0.037)→(0.545, 0.115, 0.158) | (0.497, 0.001, 0.026)→(0.555, 0.115, 0.133) | 0.266→0.097 | 1.00 / 15.667 | 0.229 | 0.457 |
| descend_release | descend | 1.00 / step_budget | (0.545, 0.115, 0.158)→(0.577, 0.178, 0.174) | (0.555, 0.115, 0.133)→(0.565, 0.148, 0.016) | 0.097→0.175 | 1.00 / 8.333 | 94251.743 | 1.466 |
| release_gripper | release | 1.00 / step_budget | (0.577, 0.178, 0.174)→(0.571, 0.176, 0.195) | (0.565, 0.148, 0.016)→(0.565, 0.148, 0.016) | 0.175→0.175 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.409
- phase_score: 0.468
- phase_breakdown.approach_1_score: 0.012
- phase_breakdown.descend_1_score: 0.868
- phase_breakdown.transport_arc_score: 0.233
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.685
- grasp_place_fitness: 0.429

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.429
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.409
- **Median Q (composite search score)**: -0.128
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.405


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12972,"descend_1.grasp_z_offset":0.01044,"descend_release.place_speed":0.10997,"lift_up.lift_up_height":0.19705,"lift_up.lift_up_speed":0.27088,"transport.transport_height":0.05099,"transport.transport_speed":0.17363},"optimized_scores":{"best_composite_score":-0.15452,"best_fitness_score":0.34548,"best_task_score":0.24322},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3182.0,"contact_point_centroid":[0.54021,0.10275,-0.00224],"force_p95":0.13601,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43338,"mean_force":0.13847,"phase_index":5.0,"phase_name":"descend_release","phase_type":"descend","tcp_position_centroid":[0.53572,0.1095,0.18039]},{"body_a":"world","body_b":"grasp_target","contact_count":197.0,"contact_point_centroid":[0.51256,-0.01607,-0.00105],"force_p95":0.27125,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53844,"mean_force":0.19123,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49932,-0.01936,0.03812]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14591.0,"contact_point_centroid":[0.512,0.03638,0.08686],"force_p95":0.10081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30344,"mean_force":0.06766,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50854,0.01765,0.08538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13818.0,"contact_point_centroid":[0.51098,-0.0036,0.08398],"force_p95":0.11033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28299,"mean_force":0.07289,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50784,0.01529,0.08223]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.51372,-0.02258,-0.00211],"force_p95":0.25227,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25295,"mean_force":0.22602,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.50041,-0.02246,0.03583]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.52779,0.05139,0.14547],"force_p95":0.18981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23712,"mean_force":0.13542,"phase_index":5.0,"phase_name":"descend_release","phase_type":"descend","tcp_position_centroid":[0.52292,0.06927,0.14909]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":854.0,"contact_point_centroid":[0.52863,0.0877,0.14576],"force_p95":0.16437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2325,"mean_force":0.1174,"phase_index":5.0,"phase_name":"descend_release","phase_type":"descend","tcp_position_centroid":[0.52303,0.07013,0.14952]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02287,-0.00205],"force_p95":0.13813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17175,"mean_force":0.12682,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50164,-0.02249,0.03718]},{"body_a":"world","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.5137,-0.02302,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50334,-0.01005,0.23399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.50102,-0.00326,0.03866],"force_p95":0.07743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12621,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50046,-0.02246,0.0359]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.50101,-0.04146,0.03766],"force_p95":0.10956,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12576,"mean_force":0.07551,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.50041,-0.02246,0.03583]},{"body_a":"world","body_b":"grasp_target","contact_count":1528.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50741,-0.02162,0.10581]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54021,0.10313,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.54177,0.13526,0.20519]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.50098,-0.00331,0.03858],"force_p95":0.11414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11721,"mean_force":0.08114,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.50041,-0.02246,0.03583]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.50107,-0.04155,0.03772],"force_p95":0.06955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09028,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50046,-0.02246,0.0359]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3146.0,"contact_point_centroid":[0.53682,0.11137,0.18416],"force_p95":0.01113,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01058,"phase_index":5.0,"phase_name":"descend_release","phase_type":"descend","tcp_position_centroid":[0.53639,0.11136,0.18195]}],"total_contact_groups":17},"final_pose_error":0.02623,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.54021,0.10313,0.01602],"final_tcp_position":[0.5454,0.13615,0.2027],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.43338,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1656.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50877,-0.02067,0.16781],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1528.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50865,-0.02266,0.04493],"tcp_start":[0.50877,-0.02067,0.16781],"tcp_to_object_dist_end":0.01958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51359,-0.02241,0.02581],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26537,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.135,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10809.0,"raw_peak_contact_force":0.17175,"subtask_id":"grasp_1","tcp_end":[0.50043,-0.02246,0.03586],"tcp_start":[0.50865,-0.02266,0.04493],"tcp_to_object_dist_end":0.01656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.51358,-0.02241,0.02578],"object_pos_start":[0.51359,-0.02241,0.02581],"object_to_goal_dist_end":0.2654,"object_to_goal_dist_start":0.26537,"object_z_max":0.02581,"peak_contact_force":0.25295,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":123.0,"raw_peak_contact_force":0.25295,"tcp_end":[0.50033,-0.02246,0.03573],"tcp_start":[0.50038,-0.02246,0.03579],"tcp_to_object_dist_end":0.01657,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53344,0.06327,0.1241],"object_pos_start":[0.51352,-0.02241,0.02567],"object_to_goal_dist_end":0.1335,"object_to_goal_dist_start":0.26549,"object_z_max":0.12403,"peak_contact_force":0.16638,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28606.0,"raw_peak_contact_force":0.53844,"subtask_id":"transport_arc","tcp_end":[0.52292,0.06321,0.14704],"tcp_start":[0.50033,-0.02246,0.03573],"tcp_to_object_dist_end":0.02524,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54021,0.10313,0.01602],"object_pos_start":[0.53344,0.06327,0.1241],"object_to_goal_dist_end":0.21207,"object_to_goal_dist_start":0.1335,"object_z_max":0.12641,"peak_contact_force":0.12263,"phase_name":"descend_release","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7906.0,"raw_peak_contact_force":1.43338,"subtask_id":"release_1","tcp_end":[0.5454,0.13615,0.2027],"tcp_start":[0.52292,0.06321,0.14704],"tcp_to_object_dist_end":0.18965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54021,0.10313,0.01602],"object_pos_start":[0.54021,0.10313,0.01602],"object_to_goal_dist_end":0.21207,"object_to_goal_dist_start":0.21207,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_gripper","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54038,0.13487,0.22553],"tcp_start":[0.5454,0.13615,0.2027],"tcp_to_object_dist_end":0.2119,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95283,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2164,"descend_1.grasp_z_offset":0.01002,"descend_release.place_speed":0.28992,"lift_up.lift_up_height":0.19422,"lift_up.lift_up_speed":0.06909,"transport.transport_height":0.07642,"transport.transport_speed":0.23136},"optimized_scores":{"best_composite_score":-0.0714,"best_fitness_score":0.4286,"best_task_score":0.40912},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2219.0,"contact_point_centroid":[0.55382,0.21711,-0.00239],"force_p95":0.16511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42017,"mean_force":0.14255,"phase_index":5.0,"phase_name":"descend_release","phase_type":"descend","tcp_position_centroid":[0.55028,0.21935,0.14263]},{"body_a":"world","body_b":"grasp_target","contact_count":267.0,"contact_point_centroid":[0.50302,0.05036,-0.0014],"force_p95":0.3244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41376,"mean_force":0.24395,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.48804,0.04791,0.03814]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.50135,0.04442,-0.00227],"force_p95":0.2734,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27477,"mean_force":0.23799,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.48849,0.04337,0.036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14029.0,"contact_point_centroid":[0.50899,0.08087,0.08515],"force_p95":0.11837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26445,"mean_force":0.07265,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50589,0.09965,0.08361]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":207.0,"contact_point_centroid":[0.54162,0.16333,0.14902],"force_p95":0.21557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24122,"mean_force":0.16796,"phase_index":5.0,"phase_name":"descend_release","phase_type":"descend","tcp_position_centroid":[0.53655,0.18119,0.15389]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04485,-0.00215],"force_p95":0.16377,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23762,"mean_force":0.13373,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48969,0.04348,0.03728]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13848.0,"contact_point_centroid":[0.51106,0.12292,0.08911],"force_p95":0.1083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2193,"mean_force":0.07154,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50761,0.10412,0.08773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":352.0,"contact_point_centroid":[0.54202,0.19923,0.14842],"force_p95":0.16828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21005,"mean_force":0.10073,"phase_index":5.0,"phase_name":"descend_release","phase_type":"descend","tcp_position_centroid":[0.53674,0.18226,0.15315]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.50118,0.04505,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49834,0.01743,0.27525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.48818,0.06258,0.03847],"force_p95":0.11039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12877,"mean_force":0.07241,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.48849,0.04337,0.036]},{"body_a":"world","body_b":"grasp_target","contact_count":2540.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49616,0.04026,0.14655]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55388,0.21721,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.55506,0.23887,0.14065]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.48837,0.02417,0.03905],"force_p95":0.10494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1225,"mean_force":0.07055,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.48849,0.04337,0.036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.48842,0.02413,0.03916],"force_p95":0.07069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11973,"mean_force":0.04299,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48854,0.04337,0.03606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5519.0,"contact_point_centroid":[0.48823,0.0627,0.03857],"force_p95":0.07039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07531,"mean_force":0.04097,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48855,0.04337,0.03607]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2039.0,"contact_point_centroid":[0.55203,0.22241,0.14442],"force_p95":0.0114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01822,"mean_force":0.01069,"phase_index":5.0,"phase_name":"descend_release","phase_type":"descend","tcp_position_centroid":[0.55155,0.22238,0.14212]}],"total_contact_groups":17},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55388,0.21721,0.01602],"final_tcp_position":[0.55932,0.24071,0.13925],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273006.15489,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":856.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49808,0.0366,0.25069],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2540.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49655,0.04409,0.0447],"tcp_start":[0.49808,0.0366,0.25069],"tcp_to_object_dist_end":0.01928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50112,0.04373,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24326,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15767,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12352.0,"raw_peak_contact_force":0.23762,"subtask_id":"grasp_1","tcp_end":[0.48851,0.04337,0.03603],"tcp_start":[0.49655,0.04409,0.0447],"tcp_to_object_dist_end":0.01644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50111,0.04373,0.02545],"object_pos_start":[0.50112,0.04373,0.02548],"object_to_goal_dist_end":0.24328,"object_to_goal_dist_start":0.24326,"object_z_max":0.02548,"peak_contact_force":0.27477,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":141.0,"raw_peak_contact_force":0.27477,"tcp_end":[0.48841,0.04336,0.0359],"tcp_start":[0.48846,0.04336,0.03596],"tcp_to_object_dist_end":0.01645,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54474,0.17833,0.13107],"object_pos_start":[0.50105,0.04372,0.02534],"object_to_goal_dist_end":0.07114,"object_to_goal_dist_start":0.24335,"object_z_max":0.13093,"peak_contact_force":0.16604,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28144.0,"raw_peak_contact_force":0.41376,"subtask_id":"transport_arc","tcp_end":[0.53611,0.17831,0.15577],"tcp_start":[0.48841,0.04336,0.0359],"tcp_to_object_dist_end":0.02616,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":668.0,"n_steps_budget":1000.0,"object_pos_end":[0.55388,0.21721,0.01602],"object_pos_start":[0.54474,0.17833,0.13107],"object_to_goal_dist_end":0.13406,"object_to_goal_dist_start":0.07114,"object_z_max":0.13113,"peak_contact_force":273006.15489,"phase_name":"descend_release","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4817.0,"raw_peak_contact_force":1.42017,"subtask_id":"release_1","tcp_end":[0.55932,0.24071,0.13925],"tcp_start":[0.53611,0.17831,0.15577],"tcp_to_object_dist_end":0.12557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55388,0.21721,0.01602],"object_pos_start":[0.55388,0.21721,0.01602],"object_to_goal_dist_end":0.13406,"object_to_goal_dist_start":0.13406,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_gripper","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5534,0.23808,0.16054],"tcp_start":[0.55932,0.24071,0.13925],"tcp_to_object_dist_end":0.14602,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81513,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29678,"descend_1.grasp_z_offset":0.01259,"descend_release.place_speed":0.08821,"lift_up.lift_up_height":0.235,"lift_up.lift_up_speed":0.26528,"transport.transport_height":0.05091,"transport.transport_speed":0.27042},"optimized_scores":{"best_composite_score":-0.12824,"best_fitness_score":0.37176,"best_task_score":0.30055},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3171.0,"contact_point_centroid":[0.60121,0.12279,-0.0023],"force_p95":0.12747,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54372,"mean_force":0.13733,"phase_index":5.0,"phase_name":"descend_release","phase_type":"descend","tcp_position_centroid":[0.60667,0.13724,0.17469]},{"body_a":"world","body_b":"grasp_target","contact_count":265.0,"contact_point_centroid":[0.48067,-0.01483,-0.00142],"force_p95":0.35587,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41921,"mean_force":0.23819,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.4655,-0.01598,0.04161]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14752.0,"contact_point_centroid":[0.5127,0.01406,0.09521],"force_p95":0.1079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35592,"mean_force":0.07007,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50966,0.03284,0.09373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14049.0,"contact_point_centroid":[0.51683,0.05563,0.09978],"force_p95":0.10756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33661,"mean_force":0.07068,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51341,0.03682,0.09813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1051.0,"contact_point_centroid":[0.58521,0.12663,0.16526],"force_p95":0.14559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27451,"mean_force":0.09759,"phase_index":5.0,"phase_name":"descend_release","phase_type":"descend","tcp_position_centroid":[0.5797,0.10894,0.16881]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":762.0,"contact_point_centroid":[0.5843,0.09009,0.16569],"force_p95":0.19751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26769,"mean_force":0.13145,"phase_index":5.0,"phase_name":"descend_release","phase_type":"descend","tcp_position_centroid":[0.57919,0.10824,0.16899]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.47617,-0.01994,-0.00209],"force_p95":0.24458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24481,"mean_force":0.22156,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46419,-0.01971,0.03958]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02008,-0.00204],"force_p95":0.13451,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17208,"mean_force":0.12589,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46534,-0.01974,0.04074]},{"body_a":"world","body_b":"grasp_target","contact_count":948.0,"contact_point_centroid":[0.47616,-0.02015,-0.00186],"force_p95":0.13702,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48728,-0.00895,0.30793]},{"body_a":"world","body_b":"grasp_target","contact_count":3356.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47376,-0.01844,0.18088]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60124,0.12272,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_gripper","phase_type":"release","tcp_position_centroid":[0.62187,0.1554,0.18088]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.46409,-0.03886,0.0415],"force_p95":0.10523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11949,"mean_force":0.07278,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46419,-0.01971,0.03958]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.46423,-0.00055,0.04196],"force_p95":0.1045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11927,"mean_force":0.07358,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46419,-0.01971,0.03958]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4843.0,"contact_point_centroid":[0.46427,-0.0005,0.04202],"force_p95":0.06734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09617,"mean_force":0.04486,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46424,-0.01972,0.03964]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5139.0,"contact_point_centroid":[0.46413,-0.03893,0.04156],"force_p95":0.066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08218,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46424,-0.01972,0.03964]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3090.0,"contact_point_centroid":[0.60867,0.13883,0.1774],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01656,"mean_force":0.01062,"phase_index":5.0,"phase_name":"descend_release","phase_type":"descend","tcp_position_centroid":[0.60824,0.13881,0.17517]}],"total_contact_groups":17},"final_pose_error":0.01124,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60124,0.12272,0.01602],"final_tcp_position":[0.62591,0.1565,0.1806],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.95058,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":948.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47741,-0.01705,0.31741],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.29141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":839.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3356.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47195,-0.01989,0.04744],"tcp_start":[0.47741,-0.01705,0.31741],"tcp_to_object_dist_end":0.02183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01979,0.02585],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28831,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13313,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11782.0,"raw_peak_contact_force":0.17208,"subtask_id":"grasp_1","tcp_end":[0.46421,-0.01972,0.03961],"tcp_start":[0.47195,-0.01989,0.04744],"tcp_to_object_dist_end":0.01816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.47605,-0.01979,0.02582],"object_pos_start":[0.47606,-0.01979,0.02585],"object_to_goal_dist_end":0.28833,"object_to_goal_dist_start":0.28831,"object_z_max":0.02585,"peak_contact_force":0.24481,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":135.0,"raw_peak_contact_force":0.24481,"tcp_end":[0.46411,-0.01971,0.03949],"tcp_start":[0.46416,-0.01971,0.03954],"tcp_to_object_dist_end":0.01816,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58594,0.10285,0.14463],"object_pos_start":[0.47599,-0.01979,0.02571],"object_to_goal_dist_end":0.08546,"object_to_goal_dist_start":0.28842,"object_z_max":0.14453,"peak_contact_force":0.35592,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29066.0,"raw_peak_contact_force":0.41921,"subtask_id":"transport_arc","tcp_end":[0.57571,0.10298,0.17112],"tcp_start":[0.46411,-0.01971,0.03949],"tcp_to_object_dist_end":0.0284,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":990.0,"n_steps_budget":1000.0,"object_pos_end":[0.60124,0.12272,0.01602],"object_pos_start":[0.58594,0.10285,0.14463],"object_to_goal_dist_end":0.18032,"object_to_goal_dist_start":0.08546,"object_z_max":0.14468,"peak_contact_force":9748.95058,"phase_name":"descend_release","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8074.0,"raw_peak_contact_force":1.54372,"subtask_id":"release_1","tcp_end":[0.62591,0.1565,0.1806],"tcp_start":[0.57571,0.10298,0.17112],"tcp_to_object_dist_end":0.16981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60124,0.12272,0.01602],"object_pos_start":[0.60124,0.12272,0.01602],"object_to_goal_dist_end":0.18032,"object_to_goal_dist_start":0.18032,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_gripper","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62031,0.15492,0.20021],"tcp_start":[0.62591,0.1565,0.1806],"tcp_to_object_dist_end":0.18796,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```